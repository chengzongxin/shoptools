import logging
import time
import random
from typing import List, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..network.request import NetworkRequest


@dataclass
class ManualProduct:
    """未上传说明书的商品数据类"""
    productId: int
    productSkcId: int
    productName: str
    productSkuSummaries: list  # 包含skuId、库存等


class ManualChecker:
    """说明书排查爬虫类"""
    
    def __init__(self, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        """初始化爬虫
        
        Args:
            logger: 日志记录器
            progress_callback: 进度回调函数
            stop_flag_callback: 停止标志回调函数
        """
        self.logger = logger
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        
        # API地址
        self.query_products_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
        self.update_stock_url = "https://agentseller.temu.com/darwin-mms/api/kiana/foredawn/sales/stock/updateMmsSkuSalesStock"
        
        self.request = NetworkRequest()
        self.page_size = 500  # 每页查询500个商品
        self.low_stock_products = []  # 记录需要手动处理的商品

        
    def random_delay(self):
        """随机延时，避免请求过于频繁"""
        time.sleep(random.uniform(0.5, 1.5))
        
    def get_all_products_without_manual(self) -> List[ManualProduct]:
        """获取所有未上传说明书的商品
        
        Returns:
            商品列表
        """
        self.logger.info("开始查询未上传说明书的商品...")
        
        page = 1
        all_products = []
        
        while True:
            # 检查是否被用户停止
            if self.stop_flag_callback():
                self.logger.info("用户手动停止查询商品。")
                break
            
            self.logger.info(f"正在查询第 {page} 页商品...")
            
            # 查询参数：库存>=1，需要上传说明书
            data = {
                "jitStockQuantitySection": {"leftValue": 1},
                "needGuideFile": True,
                "page": page,
                "pageSize": self.page_size
            }
            
            try:
                result = self.request.post(self.query_products_url, data=data)
                
                if not result or not result.get("success"):
                    error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                    self.logger.error(f"查询第 {page} 页商品失败: {error_msg}")
                    break
                
                page_data = result.get("result", {})
                page_items = page_data.get("pageItems", [])
                total = page_data.get("total", 0)
                
                if page == 1:
                    self.logger.info(f"共找到 {total} 个未上传说明书的商品")
                
                # 解析商品数据
                for item in page_items:
                    all_products.append(ManualProduct(
                        productId=item["productId"],
                        productSkcId=item["productSkcId"],
                        productName=item["productName"],
                        productSkuSummaries=item["productSkuSummaries"]
                    ))
                
                self.logger.info(f"第 {page} 页获取到 {len(page_items)} 个商品")
                
                # 检查是否还有下一页
                if page * self.page_size >= total:
                    break
                
                page += 1
                # 随机延时
                self.random_delay()
                
            except Exception as e:
                self.logger.error(f"查询第 {page} 页商品异常: {str(e)}")
                break
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"查询完成，共获取到 {len(all_products)} 个未上传说明书的商品")
        self.logger.info(f"{'='*60}\n")
        
        return all_products
    
    def set_product_stock_to_zero(self, product: ManualProduct) -> Dict:
        """将商品库存设为0
        
        Args:
            product: 商品对象
            
        Returns:
            设置结果，包含status字段标识不同状态
        """
        try:
            # 构建SKU库存变更列表
            # virtualStockDiff 是库存变化量（差值），要设为0需要传入负的当前库存数
            sku_list = []
            has_low_stock = False  # 是否有低库存SKU
            
            for sku in product.productSkuSummaries:
                # 获取当前虚拟库存
                current_stock = sku.get("virtualStock", 0)

                if current_stock == 0:
                    self.logger.info(f"SKU {sku['productSkuId']} 当前库存为 {current_stock}，跳过")
                elif 0 < current_stock <= 998:
                    has_low_stock = True
                    self.low_stock_products.append(product)
                    self.logger.debug(f"SKU {sku['productSkuId']} 当前库存为 {current_stock}，< 998，跳过自动下架")
                # 如果库存 >= 998，则设置为负数以减少到0
                elif current_stock > 998:
                    sku_list.append({
                        "productSkuId": sku["productSkuId"],
                        "virtualStockDiff": -current_stock  # 传入负数减少库存
                    })
                else:
                    # 如果当前库存已经是0或负数，跳过
                    self.logger.info(f"SKU {sku['productSkuId']} 当前库存为 {current_stock}，跳过")

            # 如果没有需要修改的SKU，直接返回成功
            if not sku_list:
                self.logger.debug(f"商品 {product.productName} 所有SKU库存已为0，无需修改")
                return {"success": True, "status": "already_zero", "errorMsg": "库存已为0"}
            
            data = {
                "productId": product.productId,
                "productSkcId": product.productSkcId,
                "skuVirtualStockChangeList": sku_list
            }
            
            result = self.request.post(self.update_stock_url, data=data)
            return result or {"success": False, "errorMsg": "无返回结果"}
            
        except Exception as e:
            self.logger.error(f"设置商品 {product.productName} 库存异常: {str(e)}")
            return {"success": False, "errorMsg": str(e)}
    
    def batch_set_stock_to_zero(self, max_workers: int = 5) -> Dict:
        """批量将商品库存设为0
        
        Args:
            max_workers: 最大线程数
            
        Returns:
            批量处理结果统计
        """
        # 1. 获取所有未上传说明书的商品
        products = self.get_all_products_without_manual()
        
        if not products:
            self.logger.warning("没有找到未上传说明书的商品")
            return {"success": 0, "failed": 0, "total": 0}
        
        total = len(products)
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"开始批量设置商品库存为0（下架）")
        self.logger.info(f"共 {total} 个商品需要处理")
        self.logger.info(f"{'='*60}\n")
        
        success_count = 0
        failed_count = 0

        # 2. 使用线程池并发设置库存
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_product = {
                executor.submit(self.set_product_stock_to_zero, product): product 
                for product in products
            }
            
            # 处理完成的任务
            for idx, future in enumerate(as_completed(future_to_product), 1):
                product = future_to_product[future]
                
                # 检查是否被用户停止
                if self.stop_flag_callback():
                    self.logger.info("用户手动停止批量设置库存。")
                    break
                
                try:
                    result = future.result()
                    if result and result.get("success"):
                        # self.logger.info(f"✓ [{idx}/{total}] {product.productName} (ID: {product.productId}) 已下架（库存设为0）")
                        success_count += 1
                    else:
                        error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                        self.logger.error(
                            f"✗ [{idx}/{total}] {product.productName} (ID: {product.productId}) 下架失败: {error_msg}")
                        failed_count += 1
                        
                except Exception as e:
                    self.logger.error(f"✗ [{idx}/{total}] {product.productName} (ID: {product.productId}) 下架异常: {str(e)}")
                    failed_count += 1
                
                # 更新进度
                if self.progress_callback:
                    self.progress_callback(idx, total)
                
                # 随机延时
                self.random_delay()
        
        # 3. 最终统计
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"批量下架完成！")
        self.logger.info(f"成功: {success_count} 个商品")
        self.logger.info(f"失败: {failed_count} 个商品")
        self.logger.info(f"总计: {total} 个商品")
        self.logger.info(f"{'='*60}\n")

        # 4. 如果有需要手动处理的商品，打印详细列表
        if self.low_stock_products:
            self.logger.info(f"\n{'=' * 60}")
            self.logger.info(f"⚠️ 以下 {len(self.low_stock_products)} 个商品库存 < 998，需要手动处理：")
            self.logger.info(f"{'=' * 60}")
            for i, prod in enumerate(self.low_stock_products, 1):
                self.logger.info(f"  {i}. ID: {prod.productId}, Name: {prod.productName}")
            self.logger.info(f"{'=' * 60}\n")

        return {
            "success": success_count,
            "failed": failed_count,
            "total": total
        }

