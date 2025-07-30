import logging
import time
import random
from typing import List, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from ..network.request import NetworkRequest

@dataclass
class StockProduct:
    """库存设置商品数据类"""
    productId: int
    productSkcId: int
    productName: str
    productSkuSummaries: list  # 包含skuId等
    createdAt: int  # 创建时间戳（毫秒）

class StockBatchSetter:
    """批量设置库存爬虫类"""
    
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        """初始化爬虫
        
        Args:
            cookie: 卖家cookie
            logger: 日志记录器
            progress_callback: 进度回调函数
            stop_flag_callback: 停止标志回调函数
        """
        self.cookie = cookie
        self.logger = logger
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        self.query_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
        self.update_url = "https://agentseller.temu.com/darwin-mms/api/kiana/foredawn/sales/stock/updateMmsSkuSalesStock"
        self.request = NetworkRequest()
        self.page_size = 100
        
    def random_delay(self):
        """随机延时"""
        time.sleep(random.uniform(0.5, 1.5))
        
    def get_all_products(self) -> List[StockProduct]:
        """获取所有待设置库存的商品
        
        Returns:
            商品列表
        """
        self.logger.info("开始获取待设置库存的商品列表...")
        page = 1
        all_products = []
        total_products = 0
        
        while True:
            # 检查是否被用户停止
            if self.stop_flag_callback():
                self.logger.info("用户手动停止获取商品列表。")
                break
                
            self.logger.info(f"正在获取第 {page} 页商品列表...")
            
            data = {
                "jitStockQuantitySection": {"leftValue": 0, "rightValue": 0},
                "skcSiteStatus": 0,
                "page": page,
                "pageSize": self.page_size
            }
            
            try:
                result = self.request.post(self.query_url, data=data)
                if not result or not result.get("success"):
                    error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                    self.logger.error(f"获取第 {page} 页商品列表失败: {error_msg}")
                    break
                    
                page_data = result["result"]
                page_items = page_data["pageItems"]
                total_products = page_data["total"]
                
                if page == 1:
                    self.logger.info(f"总共需要设置库存的商品数: {total_products}")
                
                # 解析商品数据
                for item in page_items:
                    all_products.append(StockProduct(
                        productId=item["productId"],
                        productSkcId=item["productSkcId"],
                        productName=item["productName"],
                        productSkuSummaries=item["productSkuSummaries"],
                        createdAt=item.get("createdAt", 0)  # 获取创建时间戳
                    ))
                
                self.logger.info(f"第 {page} 页获取到 {len(page_items)} 个商品")
                
                # 检查是否还有下一页
                if page * self.page_size >= total_products:
                    break
                    
                page += 1
                # 随机延时，避免请求过于频繁
                self.random_delay()
                
            except Exception as e:
                self.logger.error(f"获取第 {page} 页商品列表异常: {str(e)}")
                break
        
        self.logger.info(f"商品列表获取完成，共 {len(all_products)} 个商品")
        return all_products
        
    def set_stock(self, product: StockProduct, stock_num: int) -> Dict:
        """设置单个商品的库存
        
        Args:
            product: 商品对象
            stock_num: 要设置的库存数量
            
        Returns:
            设置结果
        """
        try:
            # 构建SKU库存变更列表
            sku_list = []
            for sku in product.productSkuSummaries:
                sku_list.append({
                    "productSkuId": sku["productSkuId"],
                    "virtualStockDiff": stock_num
                })
            
            data = {
                "productId": product.productId,
                "productSkcId": product.productSkcId,
                "skuVirtualStockChangeList": sku_list
            }
            
            result = self.request.post(self.update_url, data=data)
            return result or {"success": False, "errorMsg": "无返回结果"}
            
        except Exception as e:
            self.logger.error(f"设置商品 {product.productName} 库存异常: {str(e)}")
            return {"success": False, "errorMsg": str(e)}
        
    def batch_set_stock(self, max_workers: int = 5, days: int = 5) -> Dict:
        """批量设置库存
        
        Args:
            max_workers: 最大线程数
            days: 只处理N天内创建的商品
            
        Returns:
            批量处理结果统计
        """
        # 获取所有商品
        products = self.get_all_products()
        if not products:
            self.logger.warning("没有找到需要设置库存的商品")
            return {"success": 0, "failed": 0, "total": 0, "skipped": 0}
            
        # 按创建时间过滤商品
        now = datetime.now()
        filtered_products = []
        skipped_count = 0
        
        for product in products:
            try:
                # createdAt 是毫秒时间戳，需要转换为秒
                if product.createdAt > 0:
                    created_time = datetime.fromtimestamp(product.createdAt / 1000)
                    days_diff = (now - created_time).days
                    
                    if days_diff <= days:
                        filtered_products.append(product)
                    else:
                        self.logger.info(f"跳过商品 {product.productName} (ID: {product.productId})，创建时间超过{days}天 ({days_diff}天前)")
                        skipped_count += 1
                else:
                    # 如果没有创建时间，默认跳过
                    self.logger.warning(f"商品 {product.productName} (ID: {product.productId}) 缺少创建时间，跳过")
                    skipped_count += 1
                    
            except Exception as e:
                self.logger.error(f"处理商品 {product.productName} 创建时间时出错: {str(e)}，跳过")
                skipped_count += 1
        
        if not filtered_products:
            self.logger.warning(f"过滤后没有符合条件的商品（{days}天内创建）")
            return {"success": 0, "failed": 0, "total": 0, "skipped": skipped_count}
            
        total = len(filtered_products)
        stock_num = 1000  # 写死库存数量为1000
        self.logger.info(f"开始批量设置库存，共 {total} 个商品（跳过 {skipped_count} 个），每个商品设置 {stock_num} 库存")
        
        success_count = 0
        failed_count = 0
        
        # 使用线程池并发设置库存
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_product = {
                executor.submit(self.set_stock, product, stock_num): product 
                for product in filtered_products
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
                        self.logger.info(f"✓ {product.productName} (ID: {product.productId}) 设置库存成功")
                        success_count += 1
                    else:
                        error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                        self.logger.error(f"✗ {product.productName} (ID: {product.productId}) 设置库存失败: {error_msg}")
                        failed_count += 1
                        
                except Exception as e:
                    self.logger.error(f"✗ {product.productName} (ID: {product.productId}) 设置库存异常: {str(e)}")
                    failed_count += 1
                
                # 更新进度
                if self.progress_callback:
                    self.progress_callback(idx, total)
                
                # 随机延时，避免请求过于频繁
                self.random_delay()
        
        # 最终统计
        self.logger.info(f"批量设置库存完成！成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count}, 总计: {total}")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "skipped": skipped_count
        } 