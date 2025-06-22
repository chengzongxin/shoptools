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
        # 每次签署的最大数量限制
        self.max_batch_size = 20
        
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
            "pageSize": 100  # 获取100个，但每次只处理20个
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
        """批量处理商品 - 循环处理第一页数据，每次处理20个
            
        Returns:
            处理结果列表
        """
        results = []
        total_processed = 0
        batch_count = 0
        
        if self.stop_flag_callback():
            return []

        # 循环处理，直到没有更多待签署的商品
        while True:
            # 检查是否被用户停止
            if self.stop_flag_callback():
                self.logger.info("用户手动停止签署。")
                break
                
            # 获取当前第一页的商品列表
            self.logger.info(f"正在获取第 {batch_count + 1} 批待签署商品列表...")
            page_data = self.get_unsigned_products_page()
            
            if not page_data or not page_data.get("pageItems"):
                self.logger.info("没有更多待签署的商品了。")
                break
                
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

            current_batch_size = len(products)
            self.logger.info(f"第 {batch_count + 1} 批发现 {current_batch_size} 个待签署的商品。")
            
            if current_batch_size == 0:
                self.logger.info("当前批次没有待签署的商品，处理完成。")
                break
                
            # 限制每次最多处理20个
            if current_batch_size > self.max_batch_size:
                products = products[:self.max_batch_size]
                current_batch_size = self.max_batch_size
                self.logger.info(f"限制处理数量为 {self.max_batch_size} 个。")
            
            # 签署当前批次的商品
            if self.stop_flag_callback():
                self.logger.info("用户手动停止签署。")
                break
                
            self.logger.info(f"正在签署第 {batch_count + 1} 批的 {current_batch_size} 个商品...")
            result = self.sign_jit(products)
            
            if result:
                results.append(result)
                success_num = result.get("successNum", 0)
                total_processed += success_num
                batch_count += 1
                
                self.logger.info(f"第 {batch_count} 批签署完成，成功 {success_num} 个，累计成功 {total_processed} 个。")
                
                # 更新进度 - 这里我们显示批次进度
                if self.progress_callback:
                    self.progress_callback(batch_count, batch_count)  # 显示当前批次
            else:
                self.logger.error(f"第 {batch_count + 1} 批签署失败，跳过此批次。")
                # 即使失败也增加批次计数，避免无限循环
                batch_count += 1
                
            # 随机延时，避免请求过于频繁
            self.random_delay()
            
        # 最终统计
        if results:
            total_success = sum(r.get("successNum", 0) for r in results)
            total_failed = sum(r.get("failedNum", 0) for r in results)
            self.logger.info(f"批量签署全部完成! 总批次: {batch_count}, 总成功: {total_success}, 总失败: {total_failed}")
        else:
            self.logger.info("批量签署任务结束，没有处理任何商品。")
            
        return results 