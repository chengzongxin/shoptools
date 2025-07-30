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
    
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None):
        """初始化爬虫
        
        Args:
            cookie: 卖家cookie
            logger: 日志记录器
            progress_callback: 进度回调函数
        """
        self.logger = logger
        self.progress_callback = progress_callback
        self.query_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
        self.sign_url = "https://agentseller.temu.com/visage-agent-seller/product/agreement/batch/sign"
        self.request = NetworkRequest()
        self._stop_flag = False
        
    def random_delay(self):
        """随机延时"""
        time.sleep(random.uniform(1, 2))
            
    def stop(self):
        """停止爬虫"""
        self._stop_flag = True
        
    def get_page_data(self, page: int, page_size: int) -> Dict:
        """获取商品列表数据
        
        Args:
            page: 页码
            page_size: 每页数量
            
        Returns:
            商品列表数据
        """
        data = {
            "page": page,
            "pageSize": page_size
        }
        
        try:
            result = self.request.post(self.query_url, data=data)
            if result and result.get("success"):
                return result["result"]
            else:
                self.logger.error(f"获取商品列表失败: {result.get('errorMsg', '未知错误') if result else '无返回'}")
                return None
        except Exception as e:
            self.logger.error(f"获取商品列表异常: {str(e)}")
            return None
        
    def sign_jit(self, products: List[JitSignProduct]) -> Dict:
        """批量签署JIT协议
        
        Args:
            products: 商品列表
            
        Returns:
            签署结果
        """
        skc_list = [
            {
                "productId": p.productId,
                "productSkcId": p.productSkcId
            }
            for p in products
        ]
        data = {"skcList": skc_list}
        try:
            result = self.request.post(self.sign_url, data=data)
            if result and result.get("success"):
                return result["result"]
            else:
                self.logger.error(f"批量签署失败: {result.get('errorMsg', '未知错误') if result else '无返回'}")
                return None
        except Exception as e:
            self.logger.error(f"批量签署异常: {str(e)}")
            return None
        
    def batch_process(self, start_page: int = 1, end_page: int = 1, page_size: int = 50) -> List[Dict]:
        """批量处理商品
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
            
        Returns:
            处理结果列表
        """
        results = []
        total_processed = 0
        
        for page in range(start_page, end_page + 1):
            if self._stop_flag:
                break
                
            # 获取商品列表
            page_data = self.get_page_data(page, page_size)
            if not page_data:
                continue
                
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
            
            # 每20个商品一组进行签署
            for i in range(0, len(products), 20):
                if self._stop_flag:
                    break
                    
                batch = products[i:i+20]
                result = self.sign_jit(batch)
                
                if result:
                    results.append(result)
                    total_processed += result["successNum"]
                    
                    # 更新进度
                    if self.progress_callback:
                        self.progress_callback(total_processed)
                        
                # 随机延时
                self.random_delay()
                
        return results 