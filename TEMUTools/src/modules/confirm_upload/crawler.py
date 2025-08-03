import json
import time
import random
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from ..network.request import NetworkRequest

@dataclass
class UploadProduct:
    productId: int
    productName: str
    goodsId: int
    buyerName: str
    productCreatedAt: int
    supplierPrice: str
    extCode: str

class ConfirmUploadCrawler:
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        # 基础URL
        self.query_url = "https://agentseller.temu.com/api/kiana/mms/robin/searchForChainSupplier"
        self.confirm_url = "https://agentseller.temu.com/bg-brando-mms/goods/batchSupplierConfirm"

        # 初始化网络请求对象
        self.request = NetworkRequest()
        
        # 保存参数
        self.cookie = cookie
        self.logger = logger
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        
        # 延时配置（单位：秒）
        self.delay_config = {
            'page_request': (1, 2),      # 翻页请求延时范围
            'action': (1, 2),            # 确认操作延时范围
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
        
    def get_page_data(self, page: int, page_size: int, days_filter: int = 5) -> Dict:
        """获取指定页码的数据
        
        Args:
            page: 页码
            page_size: 每页数量
            days_filter: 过滤天数，只获取最近N天内的商品
        """
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_filter)
        
        # 转换为毫秒时间戳
        time_begin = int(start_time.timestamp() * 1000)
        time_end = int(end_time.timestamp() * 1000)
        
        payload = {
            "pageSize": page_size,
            "pageNum": page,
            "timeType": 1,  # 时间类型
            "timeBegin": time_begin,  # 开始时间戳
            "timeEnd": time_end,  # 结束时间戳
            "supplierTodoTypeList": [6],  # 6表示待确认上新
            "secondarySelectStatusList": [10]  # 10表示待创建首单
        }
        
        try:
            self.logger.info(f"正在获取第 {page} 页数据，每页 {page_size} 条，过滤最近 {days_filter} 天")
            self.logger.debug(f"请求URL: {self.query_url}")
            self.logger.debug(f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 添加翻页请求延时
            self.random_delay('page_request')
            
            result = self.request.post(self.query_url, data=payload)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                return {}
                
            return result
            
        except Exception as e:
            self.logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return {}
            
    def crawl(self, start_page: int = 1, end_page: int = 1, page_size: int = 10, days_filter: int = 5) -> List[Dict]:
        """爬取待确认上新商品列表数据
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
            days_filter: 过滤天数，只获取最近N天内的商品
            
        Returns:
            List[Dict]: 商品数据列表
        """
        all_data = []
        total_pages = end_page - start_page + 1
        
        for page in range(start_page, end_page + 1):
            if self.stop_flag_callback():
                self.logger.info("爬取已停止")
                break
                
            result = self.get_page_data(page, page_size, days_filter)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                break
                
            # 获取商品列表数据
            items = result.get('result', {}).get('dataList', [])
            if not items:
                self.logger.info("没有更多数据")
                break
                
            self.logger.info(f"响应数据条数: {len(items)}")
            
            # 转换数据格式
            upload_items = []
            for item in items:
                product_id = item.get('productId')
                self.logger.debug(f"处理商品: {product_id}")
                
                # 获取第一个SKC的数据
                skc_list = item.get('skcList', [])
                if skc_list:
                    skc = skc_list[0]
                    upload_product = UploadProduct(
                        productId=item['productId'],
                        productName=item['productName'],
                        goodsId=item['goodsId'],
                        buyerName=item.get('buyerName', ''),
                        productCreatedAt=item['productCreatedAt'],
                        supplierPrice=skc.get('supplierPrice', ''),
                        extCode=skc.get('extCode', '')
                    )
                    upload_items.append(upload_product)
                    self.logger.info(f"添加商品到待确认列表: {product_id}")
            
            self.logger.info(f"原始数据条数: {len(items)}")
            self.logger.info(f"本页待确认商品数: {len(upload_items)}")
            
            all_data.extend(upload_items)
            self.logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            # 更新进度
            if self.progress_callback:
                progress = ((page - start_page + 1) / total_pages) * 100
                self.progress_callback(progress)
            
            # 添加翻页延时
            self.random_delay('page_request')
            
        return all_data

    def confirm_upload(self, products: List[UploadProduct]) -> List[Dict]:
        """批量确认上新
        
        Args:
            products: 要确认上新的商品列表
            
        Returns:
            List[Dict]: 处理结果列表，每个结果包含商品ID、处理状态和说明
        """
        results = []
        
        try:
            # 准备请求数据
            payload = {
                "supplierConfirmReqList": [
                    {
                        "goodsId": product.goodsId
                    }
                    for product in products
                ]
            }
            
            self.logger.info(f"正在为 {len(products)} 个商品确认上新")
            self.logger.debug(f"请求URL: {self.confirm_url}")
            self.logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 添加确认请求延时
            self.random_delay('action')
            
            # 发送请求
            result = self.request.post(self.confirm_url, data=payload)
            
            if not result or not result.get('success'):
                error_msg = result.get('errorMsg', '未知错误') if result else '请求失败'
                self.logger.error(f"确认上新失败: {error_msg}")
                
                # 记录每个商品的失败结果
                for product in products:
                    results.append({
                        'productId': product.productId,
                        'goodsId': product.goodsId,
                        'success': False,
                        'message': f"确认上新失败: {error_msg}"
                    })
            else:
                # 检查失败详情
                failed_details = result.get('result', {}).get('failedDetails', [])
                failed_goods_ids = {detail.get('goodsId') for detail in failed_details}
                
                # 记录每个商品的结果
                for product in products:
                    success = product.goodsId not in failed_goods_ids
                    results.append({
                        'productId': product.productId,
                        'goodsId': product.goodsId,
                        'success': success,
                        'message': "成功确认上新" if success else "确认上新失败"
                    })
                
                self.logger.info(f"成功为 {len(products) - len(failed_details)} 个商品确认上新")
                if failed_details:
                    self.logger.warning(f"有 {len(failed_details)} 个商品确认上新失败")
            
            return results
            
        except Exception as e:
            self.logger.error(f"确认上新时发生错误: {str(e)}")
            
            # 记录每个商品的错误结果
            for product in products:
                results.append({
                    'productId': product.productId,
                    'goodsId': product.goodsId,
                    'success': False,
                    'message': f"确认上新时发生错误: {str(e)}"
                })
            
            return results
            
    def batch_process(self, days_filter: int = 5) -> List[Dict]:
        """批量处理确认上新（循环处理第一页直到完成）
        
        Args:
            days_filter: 过滤天数，只获取最近N天内的商品
            
        Returns:
            List[Dict]: 处理结果列表，每个结果包含商品ID、处理状态和说明
        """
        results = []
        total_processed = 0
        
        try:
            while True:
                if self.stop_flag_callback():
                    self.logger.info("批量处理已停止")
                    break
                    
                self.logger.info(f"正在获取第一页待确认上新商品（过滤最近 {days_filter} 天）...")
                
                # 获取第一页数据
                result = self.get_page_data(1, 20, days_filter)  # 固定获取第一页，每页20条, 注意如果设置多了会报错400，之前设置的是100，接口报错400，所以这里设置20
                if not result:
                    self.logger.error("第一页数据获取失败")
                    break
                    
                # 获取商品列表数据
                items = result.get('result', {}).get('dataList', [])
                if not items:
                    self.logger.info("第一页没有待确认上新的商品，所有商品已处理完成")
                    break
                    
                # 转换数据格式
                upload_items = []
                for item in items:
                    if self.stop_flag_callback():
                        self.logger.info("用户手动停止处理")
                        break
                        
                    # 获取第一个SKC的数据
                    skc_list = item.get('skcList', [])
                    if skc_list:
                        skc = skc_list[0]
                        upload_product = UploadProduct(
                            productId=item['productId'],
                            productName=item['productName'],
                            goodsId=item['goodsId'],
                            buyerName=item.get('buyerName', ''),
                            productCreatedAt=item['productCreatedAt'],
                            supplierPrice=skc.get('supplierPrice', ''),
                            extCode=skc.get('extCode', '')
                        )
                        upload_items.append(upload_product)
                        
                        # 打印商品详细信息
                        self.logger.info(f"待确认上新商品信息:")
                        self.logger.info(f"商品ID: {upload_product.productId}")
                        self.logger.info(f"商品名称: {upload_product.productName}")
                        self.logger.info(f"货号: {upload_product.extCode}")
                        self.logger.info(f"价格: {upload_product.supplierPrice}")
                        self.logger.info(f"买家: {upload_product.buyerName}")
                        self.logger.info(f"创建时间: {datetime.fromtimestamp(upload_product.productCreatedAt/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                        self.logger.info("-" * 50)
                            
                if not upload_items:
                    self.logger.info("第一页没有需要确认上新的商品，所有商品已处理完成")
                    break
                    
                # 处理确认上新
                self.logger.info(f"第一页共有 {len(upload_items)} 个商品需要确认上新")
                
                if self.stop_flag_callback():
                    self.logger.info("用户手动停止处理")
                    break
                    
                page_results = self.confirm_upload(upload_items)
                results.extend(page_results)
                
                # 统计本批次结果
                success_count = sum(1 for r in page_results if r['success'])
                total_processed += success_count
                self.logger.info(f"本批次处理完成，成功 {success_count} 个，累计成功 {total_processed} 个")
                
                # 更新进度（这里用循环次数来模拟进度）
                if self.progress_callback:
                    # 由于不知道总数量，我们用循环次数来显示进度
                    # 每处理一批次，进度增加10%，最大到90%
                    progress = min(90, len(results) // 20 * 10)
                    self.progress_callback(progress)
                
                # 批次间延时
                self.random_delay('page_request')
                
            # 完成时设置进度为100%
            if self.progress_callback:
                self.progress_callback(100)
                
            self.logger.info(f"批量处理完成，总共处理 {total_processed} 个商品")
            return results
            
        except Exception as e:
            self.logger.error(f"批量处理确认上新时发生错误: {str(e)}")
            return results 