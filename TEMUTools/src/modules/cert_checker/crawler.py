import logging
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..network.request import NetworkRequest


@dataclass
class CertType:
    """资质类型数据类"""
    id: int
    name: str


@dataclass
class CertProduct:
    """需要资质的商品数据类"""
    productId: int
    productSkcId: int
    productName: str
    productSkuSummaries: list  # 包含skuId等
    requireCertTypes: list  # 需要的资质类型


class CertChecker:
    """资质排查爬虫类"""
    
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
        self.cert_types_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/certTypeEnum"
        self.query_products_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
        self.update_stock_url = "https://agentseller.temu.com/darwin-mms/api/kiana/foredawn/sales/stock/updateMmsSkuSalesStock"
        
        self.request = NetworkRequest()
        self.page_size = 500  # 每页查询500个商品
        self.max_cert_types_per_request = 500  # 每次最多查询500个资质类型
        
    def random_delay(self):
        """随机延时，避免请求过于频繁"""
        time.sleep(random.uniform(0.5, 1.5))
        
    def get_all_cert_types(self) -> List[CertType]:
        """获取所有资质类型（排除GCC）
        
        Returns:
            资质类型列表
        """
        self.logger.info("开始获取所有资质类型...")
        
        try:
            result = self.request.post(self.cert_types_url, data={})
            
            if not result or not result.get("success"):
                error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                self.logger.error(f"获取资质类型失败: {error_msg}")
                return []
            
            enum_list = result.get("result", {}).get("enumList", [])
            
            # 过滤掉GCC (id=28)
            cert_types = []
            gcc_filtered = False
            
            for item in enum_list:
                cert_id = item.get("id")
                cert_name = item.get("name")
                
                if cert_id == 28:
                    self.logger.info(f"排除GCC资质 (ID: 28, Name: {cert_name})")
                    gcc_filtered = True
                    continue
                
                cert_types.append(CertType(
                    id=cert_id,
                    name=cert_name
                ))
            
            self.logger.info(f"获取到 {len(cert_types)} 个资质类型（已排除GCC）")
            
            if gcc_filtered:
                self.logger.info("✓ 已成功排除GCC资质")
            
            return cert_types
            
        except Exception as e:
            self.logger.error(f"获取资质类型异常: {str(e)}")
            return []
    
    def get_products_by_cert_types(self, cert_type_ids: List[int]) -> List[CertProduct]:
        """根据资质类型查询商品
        
        Args:
            cert_type_ids: 资质类型ID列表（最多500个）
            
        Returns:
            商品列表
        """
        self.logger.info(f"开始查询需要资质的商品，资质类型数: {len(cert_type_ids)}")
        
        page = 1
        all_products = []
        
        while True:
            # 检查是否被用户停止
            if self.stop_flag_callback():
                self.logger.info("用户手动停止查询商品。")
                break
            
            self.logger.info(f"正在查询第 {page} 页商品...")
            
            data = {
                "requireCertTypes": cert_type_ids,
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
                    self.logger.info(f"本批次共找到 {total} 个需要资质的商品")
                
                # 解析商品数据
                for item in page_items:
                    all_products.append(CertProduct(
                        productId=item["productId"],
                        productSkcId=item["productSkcId"],
                        productName=item["productName"],
                        productSkuSummaries=item["productSkuSummaries"],
                        requireCertTypes=item.get("requireCertTypes", [])
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
        
        self.logger.info(f"本批次查询完成，共获取到 {len(all_products)} 个商品")
        return all_products
    
    def get_all_cert_products(self) -> List[CertProduct]:
        """获取所有需要资质的商品（分批查询）
        
        Returns:
            所有商品列表
        """
        # 1. 获取所有资质类型
        cert_types = self.get_all_cert_types()
        
        if not cert_types:
            self.logger.warning("没有获取到资质类型")
            return []
        
        # 2. 分批查询商品（每批最多500个资质类型）
        all_products = []
        total_cert_types = len(cert_types)
        batch_count = (total_cert_types + self.max_cert_types_per_request - 1) // self.max_cert_types_per_request
        
        self.logger.info(f"共 {total_cert_types} 个资质类型，需要分 {batch_count} 批次查询")
        
        for i in range(0, total_cert_types, self.max_cert_types_per_request):
            # 检查是否被用户停止
            if self.stop_flag_callback():
                self.logger.info("用户手动停止查询。")
                break
            
            batch_cert_types = cert_types[i:i + self.max_cert_types_per_request]
            batch_cert_ids = [cert.id for cert in batch_cert_types]
            
            batch_num = i // self.max_cert_types_per_request + 1
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"开始第 {batch_num}/{batch_count} 批次查询")
            self.logger.info(f"本批次资质类型数: {len(batch_cert_ids)}")
            self.logger.info(f"{'='*60}\n")
            
            # 查询本批次的商品
            batch_products = self.get_products_by_cert_types(batch_cert_ids)
            
            if batch_products:
                all_products.extend(batch_products)
                self.logger.info(f"✓ 第 {batch_num} 批次完成，本批次获取 {len(batch_products)} 个商品")
            else:
                self.logger.info(f"第 {batch_num} 批次没有找到商品")
            
            # 批次间随机延时
            if batch_num < batch_count:
                self.random_delay()
        
        # 3. 去重（同一个商品可能出现在不同批次中）
        unique_products = {}
        for product in all_products:
            product_id = product.productId
            if product_id not in unique_products:
                unique_products[product_id] = product
        
        result_products = list(unique_products.values())
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"所有批次查询完成！")
        self.logger.info(f"总共获取: {len(all_products)} 个商品记录")
        self.logger.info(f"去重后: {len(result_products)} 个唯一商品")
        self.logger.info(f"{'='*60}\n")
        
        return result_products
    
    def set_product_stock_to_zero(self, product: CertProduct) -> Dict:
        """将商品库存设为0
        
        Args:
            product: 商品对象
            
        Returns:
            设置结果
        """
        try:
            # 构建SKU库存变更列表
            # virtualStockDiff 是库存变化量（差值），要设为0需要传入负的当前库存数
            sku_list = []
            for sku in product.productSkuSummaries:
                # 获取当前虚拟库存
                current_stock = sku.get("virtualStock", 0)
                
                # 如果当前库存大于0，则设置为负数以减少到0
                if current_stock > 0:
                    sku_list.append({
                        "productSkuId": sku["productSkuId"],
                        "virtualStockDiff": -current_stock  # 传入负数减少库存
                    })
                else:
                    # 如果当前库存已经是0或负数，跳过
                    self.logger.debug(f"SKU {sku['productSkuId']} 当前库存为 {current_stock}，跳过")
            
            # 如果没有需要修改的SKU，直接返回成功
            if not sku_list:
                self.logger.info(f"商品 {product.productName} 所有SKU库存已为0，无需修改")
                return {"success": True, "errorMsg": "库存已为0"}
            
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
        # 1. 获取所有需要资质的商品
        products = self.get_all_cert_products()
        
        if not products:
            self.logger.warning("没有找到需要资质的商品")
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
                        self.logger.info(f"✓ [{idx}/{total}] {product.productName} (ID: {product.productId}) 已下架（库存设为0）")
                        success_count += 1
                    else:
                        error_msg = result.get('errorMsg', '未知错误') if result else '无返回'
                        self.logger.error(f"✗ [{idx}/{total}] {product.productName} (ID: {product.productId}) 下架失败: {error_msg}")
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
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": total
        }

