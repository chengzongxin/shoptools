import logging
import time
import random
from typing import Dict, List
from dataclasses import dataclass
from ..network.request import NetworkRequest

@dataclass
class JitSignProduct:
    """JIT签署商品数据类"""
    productId: int
    productSkcId: int
    productName: str
    skcStatus: int
    productJitMode: Dict

class JitSignCrawler:
    """JIT签署爬虫类"""
    
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        """初始化爬虫
        
        Args:
            cookie: 卖家cookie
            logger: 日志记录器
            progress_callback: 进度回调函数
            stop_flag_callback: 停止标志回调函数
        """
        self.logger = logger
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        self.base_url = "https://seller.kuajingmaihuo.com/bg-visage-mms"
        self.request = NetworkRequest()
        
    def random_delay(self):
        """随机延时"""
        time.sleep(random.uniform(1, 2))
            
    def get_unsigned_products_page(self) -> Dict:
        """获取待签署商品列表数据
        
        Returns:
            商品列表数据
        """
        url = f"{self.base_url}/product/skc/pageQuery"
        data = {
            "skcJitStatus": 3,
            "page": 1,
            "pageSize": 100
        }
        
        try:
            result = self.request.post(url, data=data)
            if result and result.get("success"):
                return result["result"]
            else:
                self.logger.error(f"获取待签署商品列表失败: {result.get('errorMsg', '未知错误') if result else '无返回'}")
                return None
        except Exception as e:
            self.logger.error(f"获取待签署商品列表异常: {str(e)}")
            return None
        
    def sign_jit(self, products: List[JitSignProduct]) -> Dict:
        """批量签署JIT协议
        
        Args:
            products: 商品列表
            
        Returns:
            签署结果
        """
        url = f"{self.base_url}/product/agreement/batch/sign"
        skc_list = [
            {
                "productId": p.productId,
                "productSkcId": p.productSkcId
            }
            for p in products
        ]
        data = {"skcList": skc_list}
        try:
            result = self.request.post(url, data=data)
            if result and result.get("success"):
                return result["result"]
            else:
                self.logger.error(f"批量签署失败: {result.get('errorMsg', '未知错误') if result else '无返回'}")
                return None
        except Exception as e:
            self.logger.error(f"批量签署异常: {str(e)}")
            return None
        
    def batch_process(self) -> List[Dict]:
        """批量处理商品
            
        Returns:
            处理结果列表
        """
        results = []
        total_processed = 0
        
        if self.stop_flag_callback():
            return []

        # 获取商品列表
        self.logger.info("正在获取待签署商品列表...")
        page_data = self.get_unsigned_products_page()
        if not page_data or not page_data.get("pageItems"):
            self.logger.info("未找到待签署的商品。")
            return []
            
        # 解析商品数据
        products = [
            JitSignProduct(
                productId=item["productId"],
                productSkcId=item["productSkcId"],
                productName=item["productName"],
                skcStatus=item["skcStatus"],
                productJitMode=item["productJitMode"]
            )
            for item in page_data["pageItems"]
        ]

        total_to_process = len(products)
        self.logger.info(f"共发现 {total_to_process} 个待签署的商品。")
        
        if self.progress_callback:
            self.progress_callback(0, total_to_process)
            
        # 直接签署所有商品
        if self.stop_flag_callback():
            self.logger.info("用户手动停止签署。")
            return []
            
        self.logger.info(f"正在签署 {total_to_process} 个商品...")
        result = self.sign_jit(products)
        
        if result:
            results.append(result)
            success_num = result.get("successNum", 0)
            total_processed = success_num
            self.logger.info(f"签署完成，成功 {success_num} 个。")
            
            # 更新进度
            if self.progress_callback:
                self.progress_callback(total_processed, total_to_process)
                
        # 随机延时
        self.random_delay()
            
        return results 