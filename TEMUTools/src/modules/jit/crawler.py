import json
import time
import random
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from ..network.request import NetworkRequest

@dataclass
class JitProduct:
    productId: int
    productName: str
    skcId: int
    extCode: str
    supplierPrice: str
    buyerName: str
    productCreatedAt: int
    applyJitStatus: int

class JitCrawler:
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/marvel-mms/cn/api/kiana/xmen/select/searchForChainSupplier"
        self.open_jit_url = f"{self.base_url}/bg-visage-mms/product/skc/batchOpenJit"
        
        # 初始化网络请求对象
        self.request = NetworkRequest()
        
        # 保存参数
        self.cookie = cookie
        self.logger = logger
        self.progress_callback = progress_callback
        
        # 停止标志回调
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        
        # 延时配置（单位：秒）
        self.delay_config = {
            'page_request': (1, 2),      # 翻页请求延时范围
            'action': (1, 2),            # 开通JIT操作延时范围
            'between_items': (1, 2)      # 处理商品之间的延时范围
        }
        
    def random_delay(self, delay_type: str):
        """随机延时
        
        Args:
            delay_type: 延时类型，对应delay_config中的键
        """
        if delay_type in self.delay_config:
            min_delay, max_delay = self.delay_config[delay_type]
            delay = random.uniform(min_delay, max_delay)
            self.logger.debug(f"随机延时 {delay:.2f} 秒 ({delay_type})")
            time.sleep(delay)
        
    def get_page_data(self, page: int, page_size: int) -> Dict:
        """获取指定页码的数据"""
        payload = {
            "pageSize": page_size,
            "pageNum": page,
            "supplierTodoTypeList": []
        }
        
        try:
            self.logger.info(f"正在获取第 {page} 页数据，每页 {page_size} 条")
            self.logger.debug(f"请求URL: {self.api_url}")
            self.logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 添加翻页请求延时
            self.random_delay('page_request')
            
            result = self.request.post(self.api_url, data=payload)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                return None
                
            return result
            
        except Exception as e:
            self.logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return None
            
    def crawl(self, start_page: int = 1, end_page: int = 1, page_size: int = 10) -> List[Dict]:
        """爬取商品列表数据
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
            
        Returns:
            List[Dict]: 商品数据列表
        """
        all_data = []
        total_pages = end_page - start_page + 1
        
        for page in range(start_page, end_page + 1):
            if self.stop_flag_callback():
                self.logger.info("爬取已停止")
                break
                
            result = self.get_page_data(page, page_size)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                break
                
            # 获取商品列表数据
            items = result.get('result', {}).get('dataList', [])
            if not items:
                self.logger.info("没有更多数据")
                break
                
            self.logger.info(f"响应数据条数: {len(items)}")
            
            # 过滤出未开通JIT的商品
            jit_items = []
            for item in items:
                product_id = item.get('productId')
                self.logger.debug(f"处理商品: {product_id}")
                
                # 检查每个SKC的JIT状态
                for skc in item.get('skcList', []):
                    jit_status = skc.get('applyJitStatus')
                    self.logger.debug(f"商品 {product_id} 的SKC {skc.get('skcId')} JIT状态: {jit_status}")
                    
                    if jit_status == 1:  # 1表示未开通JIT
                        jit_items.append(item)
                        self.logger.info(f"添加商品到JIT列表: {product_id}")
                        break  # 找到一个未开通的SKC就跳出循环
            
            self.logger.info(f"原始数据条数: {len(items)}")
            self.logger.info(f"本页JIT商品数: {len(jit_items)}")
            
            all_data.extend(jit_items)
            self.logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            # 更新进度
            if self.progress_callback:
                progress = ((page - start_page + 1) / total_pages) * 100
                self.progress_callback(progress)
            
            # 添加翻页延时
            self.random_delay('page_request')
            
        return all_data

    def open_jit(self, products: List[JitProduct]) -> List[Dict]:
        """批量开通JIT
        
        Args:
            products: 要开通JIT的商品列表
            
        Returns:
            List[Dict]: 处理结果列表，每个结果包含商品ID、处理状态和说明
        """
        results = []
        
        try:
            # 准备请求数据
            payload = {
                "productSkcSubSellModeReqList": [
                    {
                        "productId": product.productId,
                        "productSkcId": product.skcId
                    }
                    for product in products
                ]
            }
            
            self.logger.info(f"正在为 {len(products)} 个商品开通JIT")
            self.logger.debug(f"请求URL: {self.open_jit_url}")
            self.logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 添加开通JIT请求延时
            self.random_delay('action')
            
            # 发送请求
            result = self.request.post(self.open_jit_url, data=payload)
            
            if not result or not result.get('success'):
                error_msg = result.get('errorMsg', '未知错误') if result else '请求失败'
                self.logger.error(f"开通JIT失败: {error_msg}")
                
                # 记录每个商品的失败结果
                for product in products:
                    results.append({
                        'productId': product.productId,
                        'skcId': product.skcId,
                        'success': False,
                        'message': f"开通JIT失败: {error_msg}"
                    })
            else:
                # 记录每个商品的成功结果
                for product in products:
                    results.append({
                        'productId': product.productId,
                        'skcId': product.skcId,
                        'success': True,
                        'message': "成功开通JIT"
                    })
                
                self.logger.info(f"成功为 {len(products)} 个商品开通JIT")
            
            return results
            
        except Exception as e:
            self.logger.error(f"开通JIT时发生错误: {str(e)}")
            
            # 记录每个商品的错误结果
            for product in products:
                results.append({
                    'productId': product.productId,
                    'skcId': product.skcId,
                    'success': False,
                    'message': f"开通JIT时发生错误: {str(e)}"
                })
            
            return results
            
    def batch_process(self, start_page: int = 1, end_page: int = 1, page_size: int = 50) -> List[Dict]:
        """批量处理JIT开通
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
            
        Returns:
            List[Dict]: 处理结果列表，每个结果包含商品ID、处理状态和说明
        """
        results = []
        total_pages = end_page - start_page + 1
        
        try:
            # 逐页处理
            for page in range(start_page, end_page + 1):
                if self.stop_flag_callback():
                    self.logger.info("批量处理已停止")
                    break
                    
                self.logger.info(f"正在处理第 {page} 页数据")
                
                # 获取当前页数据
                result = self.get_page_data(page, page_size)
                if not result:
                    self.logger.error(f"第 {page} 页数据获取失败")
                    continue
                    
                # 获取商品列表数据
                items = result.get('result', {}).get('dataList', [])
                if not items:
                    self.logger.info("没有更多数据")
                    break
                    
                # 过滤出需要开通JIT的商品
                jit_items = []
                for item in items:
                    for skc in item.get('skcList', []):
                        if skc.get('applyJitStatus') == 1:  # 未开通JIT
                            jit_product = JitProduct(
                                productId=item['productId'],
                                productName=item['productName'],
                                skcId=skc['skcId'],
                                extCode=skc.get('extCode', ''),
                                supplierPrice=skc.get('supplierPrice', ''),
                                buyerName=item.get('buyerName', ''),
                                productCreatedAt=item['productCreatedAt'],
                                applyJitStatus=skc.get('applyJitStatus', 0)
                            )
                            jit_items.append(jit_product)
                            
                            # 打印商品详细信息
                            # self.logger.info(f"待开通JIT商品信息:")
                            # self.logger.info(f"商品ID: {jit_product.productId}")
                            # self.logger.info(f"商品名称: {jit_product.productName}")
                            # self.logger.info(f"SKC ID: {jit_product.skcId}")
                            # self.logger.info(f"货号: {jit_product.extCode}")
                            # self.logger.info(f"价格: {jit_product.supplierPrice}")
                            # self.logger.info(f"买家: {jit_product.buyerName}")
                            # self.logger.info(f"创建时间: {datetime.fromtimestamp(jit_product.productCreatedAt/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                            # self.logger.info("-" * 50)
                            break  # 只取第一个SKC
                            
                if not jit_items:
                    self.logger.info(f"第 {page} 页没有需要开通JIT的商品")
                    continue
                    
                # 处理当前页的JIT开通
                self.logger.info(f"第 {page} 页共有 {len(jit_items)} 个商品需要开通JIT")
                page_results = self.open_jit(jit_items)
                results.extend(page_results)
                
                # 更新进度
                if self.progress_callback:
                    progress = ((page - start_page + 1) / total_pages) * 100
                    self.progress_callback(progress)
                    
                # 添加翻页请求延时
                self.random_delay('page_request')
                
            return results
            
        except Exception as e:
            self.logger.error(f"批量处理JIT开通时发生错误: {str(e)}")
            return results 