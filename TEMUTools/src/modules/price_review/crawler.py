import json
import time
import random
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from ..network.request import NetworkRequest
from .config import get_price_threshold

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProductProperty:
    important: bool
    name: str
    value: str

@dataclass
class SkuProperty:
    name: str
    value: str

@dataclass
class ProductSku:
    skuId: int
    supplierPrice: str
    supplierPriceValue: int
    extCode: str
    productPropertyList: List[SkuProperty]
    skuPreviewImage: str
    len: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    weight: Optional[int] = None
    goodsSkuId: Optional[int] = None
    priceReviewStatus: Optional[int] = None
    sensitiveList: Optional[List[int]] = None
    hasUploadBom: Optional[bool] = None
    stock: Optional[int] = None

@dataclass
class StatusTime:
    unPublishedTime: Optional[int]
    priceVerificationTime: Optional[int]
    addedToSiteTime: Optional[int]
    samplePostingFinishedTime: Optional[int]
    selectedTime: Optional[int]
    firstPurchaseTime: Optional[int]
    createdTime: Optional[int]
    samplePostTime: Optional[int]
    qcCompletedTime: Optional[int]
    terminatedTime: Optional[int]

@dataclass
class GoodsInfoStatus:
    siteVersion: Optional[str]
    confirmOperator: Optional[str]
    supplierGoodsInfoModifyStatus: Optional[int]
    deadLineTime: Optional[int]
    confirmTime: Optional[int]
    supplierConfirmStatus: int

@dataclass
class PriceReviewInfo:
    orderType: int
    priceOrderId: int
    times: int
    productSkuList: List[Dict]
    daysToConfirmLeft: Optional[int]
    siteList: Optional[List[str]]
    status: int

@dataclass
class ProductSkc:
    skcId: int
    approveStatus: int
    supplierPrice: str
    extCode: str
    previewImgUrlList: List[str]
    skuList: List[ProductSku]
    supplierPriceReviewInfoList: List[PriceReviewInfo]
    selectStatus: int
    goodsSkcId: int
    statusTime: StatusTime
    selectId: int
    buyerUid: int
    productFlowAllowanceStatus: int
    productCertStatus: int
    sampleQcType: int
    goodsLabelName: str
    applyJitStatus: int
    permittedToRePostSample: bool
    colorName: Optional[str] = None
    primaryMultiColor: Optional[str] = None
    supplierPriceCurrencyType: Optional[str] = None
    sampleType: Optional[int] = None
    pictureReviewAccepted: Optional[bool] = None
    defaultSelectedSkuList: Optional[List[int]] = None
    buyerSelectedSkuList: Optional[List[int]] = None
    buyerName: Optional[str] = None

@dataclass
class Product:
    productId: int
    productName: str
    supplierPrice: str
    leafCategoryName: str
    fullCategoryName: List[str]
    carouselImageUrlList: List[str]
    productPropertyList: List[ProductProperty]
    skcList: List[ProductSkc]
    buyerName: str
    supplierName: str
    productCreatedAt: int
    productUpdatedAt: int
    productSource: int
    supplierPriceCurrencyType: str
    catIdList: List[int]
    goodsId: int
    supplierId: int
    leafCategoryId: int
    goodsInfoStatus: GoodsInfoStatus
    isDress: bool
    isSemiHostedProduct: bool
    flowSubsidyGet: bool
    canChangeBuyer: Optional[bool] = None
    siteInfoList: Optional[List[str]] = None
    hasToConfirmPriceReviewOrder: Optional[bool] = None
    marketProductSearchLimitEndTime: Optional[int] = None
    marketProductSearchLimitTag: Optional[int] = None
    activateType: Optional[int] = None
    ifLimitNew: Optional[int] = None
    manualOperationPermitted: Optional[bool] = None
    isAsianCode: Optional[bool] = None
    mustSkipSample: Optional[bool] = None
    sampleNeeded: Optional[bool] = None
    isShoes: Optional[bool] = None
    isInAdvanceLabelWhiteList: Optional[bool] = None
    supplierScore: Optional[float] = None
    ifOpenLimitNewSwitch: Optional[bool] = None
    hasActivateButton: Optional[bool] = None
    isAllSitesPunished: Optional[bool] = None
    isAutoBidding: Optional[bool] = None
    isCertsPassed: Optional[bool] = None
    isSheinBsr: Optional[bool] = None
    hasSkcSelected: Optional[bool] = None
    isAiExperimentJoinWaitConfirm: Optional[bool] = None

@dataclass
class PriceReviewSuggestion:
    rejectRemark: str
    supplyPrice: int
    priceCurrency: str
    suggestSupplyPrice: int
    suggestPriceCurrency: str
    needEditBomInfo: bool
    canAppeal: bool
    canAppealTime: Optional[int] = None

class PriceReviewCrawler:
    def __init__(self, cookie: str, logger: logging.Logger, progress_callback=None):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/marvel-mms/cn/api/kiana/xmen/select/searchForChainSupplier"
        self.price_review_url = f"{self.base_url}/gmp/bg/magneto/api/price-review-order/no-bom/reject-remark"
        self.accept_price_url = f"{self.base_url}/marvel-mms/cn/api/kiana/magneto/price/bargain-no-bom"
        self.reject_price_url = f"{self.base_url}/gmp/bg/magneto/api/price-review-order/no-bom/review"
        
        # 初始化网络请求对象
        self.request = NetworkRequest()
        
        # 保存参数
        self.cookie = cookie
        self.logger = logger
        self.progress_callback = progress_callback
        
        # 分页参数
        self.page_size = 10
        self.current_page = 1
        
        # 停止标志
        self._stop_flag = False
        
        # 延时配置（单位：秒）
        self.delay_config = {
            'page_request': (1, 2),      # 翻页请求延时范围
            'review_info': (1, 2),       # 获取核价信息延时范围
            'action': (1, 2),            # 同意/拒绝操作延时范围
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
        
    def stop(self):
        """停止爬取"""
        self._stop_flag = True
        
    def get_page_data(self, page: int, page_size: int) -> Dict:
        """获取指定页码的数据"""
        payload = {
            "pageSize": page_size,
            "pageNum": page,
            "supplierTodoTypeList": [1]
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
            
    def crawl(self, start_page: int = 1, end_page: int = 1, page_size: int = 50) -> List[Dict]:
        """爬取待核价商品列表数据
        
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
            if self._stop_flag:
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
                
            all_data.extend(items)
            self.logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            # 更新进度
            if self.progress_callback:
                progress = ((page - start_page + 1) / total_pages) * 100
                self.progress_callback(progress)
            
            # 添加翻页请求延时
            self.random_delay('page_request')
            
        return all_data

    def get_price_review_suggestion(self, order_id: int) -> Optional[PriceReviewSuggestion]:
        """获取核价建议
        
        Args:
            order_id: 核价订单ID
            
        Returns:
            PriceReviewSuggestion: 核价建议信息，如果获取失败则返回None
        """
        try:
            self.logger.info(f"正在获取订单 {order_id} 的核价建议")
            
            payload = {
                "orderId": order_id
            }
            
            # 添加获取核价信息延时
            self.random_delay('review_info')
            
            result = self.request.post(self.price_review_url, data=payload)
            
            if not result or not result.get('success'):
                self.logger.error(f"获取订单 {order_id} 的核价建议失败")
                return None
                
            suggestion_data = result.get('result', {})
            
            return PriceReviewSuggestion(
                rejectRemark=suggestion_data.get('rejectRemark', ''),
                supplyPrice=suggestion_data.get('supplyPrice', 0),
                priceCurrency=suggestion_data.get('priceCurrency', 'CNY'),
                suggestSupplyPrice=suggestion_data.get('suggestSupplyPrice', 0),
                suggestPriceCurrency=suggestion_data.get('suggestPriceCurrency', 'CNY'),
                needEditBomInfo=suggestion_data.get('needEditBomInfo', False),
                canAppeal=suggestion_data.get('canAppeal', False),
                canAppealTime=suggestion_data.get('canAppealTime')
            )
            
        except Exception as e:
            self.logger.error(f"获取核价建议时发生错误: {str(e)}")
            return None 

    def accept_price_review(self, price_order_id: int, product_sku_id: int, price: int) -> bool:
        """同意核价建议
        
        Args:
            price_order_id: 核价订单ID
            product_sku_id: 商品SKU ID
            price: 同意后的价格
            
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info(f"正在同意核价建议，订单ID: {price_order_id}, SKU ID: {product_sku_id}, 价格: {price}")
            
            payload = {
                "supplierResult": 1,
                "priceOrderId": price_order_id,
                "items": [
                    {
                        "productSkuId": product_sku_id,
                        "price": price
                    }
                ],
                "bargainReasonList": []
            }
            
            # 添加操作延时
            self.random_delay('action')
            
            result = self.request.post(self.accept_price_url, data=payload)
            
            if not result or not result.get('success'):
                self.logger.error(f"同意核价建议失败: {result.get('errorMsg', '未知错误')}")
                return False
                
            self.logger.info("同意核价建议成功")
            return True
            
        except Exception as e:
            self.logger.error(f"同意核价建议时发生错误: {str(e)}")
            return False 

    def reject_price_review(self, price_order_id: int) -> bool:
        """拒绝核价建议
        
        Args:
            price_order_id: 核价订单ID
            
        Returns:
            bool: 是否成功
        """
        try:
            self.logger.info(f"正在拒绝核价建议，订单ID: {price_order_id}")
            
            payload = {
                "priceOrderId": price_order_id
            }
            
            # 添加操作延时
            self.random_delay('action')
            
            result = self.request.post(self.reject_price_url, data=payload)
            
            if not result or not result.get('success'):
                self.logger.error(f"拒绝核价建议失败: {result.get('errorMsg', '未知错误')}")
                return False
                
            self.logger.info("拒绝核价建议成功")
            return True
            
        except Exception as e:
            self.logger.error(f"拒绝核价建议时发生错误: {str(e)}")
            return False 

    def process_price_review(self, product_data: Dict) -> Tuple[bool, str]:
        """处理单个商品的核价
        
        Args:
            product_data: 商品数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 处理结果说明)
        """
        try:
            # 获取核价订单ID和SKU ID
            price_order_id = None
            product_sku_id = None
            ext_code = None
            
            for skc in product_data.get('skcList', []):
                for review_info in skc.get('supplierPriceReviewInfoList', []):
                    if review_info.get('status') == 1:  # 待核价状态
                        price_order_id = review_info.get('priceOrderId')
                        if skc.get('skuList'):
                            product_sku_id = skc['skuList'][0].get('skuId')
                            ext_code = skc['skuList'][0].get('extCode')
                        break
                if price_order_id and product_sku_id:
                    break
                    
            if not price_order_id or not product_sku_id:
                return False, "没有待核价的订单或SKU"
                
            # 获取核价建议
            suggestion = self.get_price_review_suggestion(price_order_id)
            if not suggestion:
                return False, "获取核价建议失败"
                
            # 获取价格底线
            threshold = get_price_threshold(ext_code)
            if threshold is None:
                return False, f"未找到商品 {ext_code} 的价格底线规则"
                
            # 将价格底线转换为分
            threshold_cents = int(threshold * 100)
            
            # 比较价格
            if suggestion.suggestSupplyPrice < threshold_cents:
                # 价格低于底线，拒绝
                if self.reject_price_review(price_order_id):
                    message = f"已拒绝核价建议，建议价格 {suggestion.suggestSupplyPrice/100}元 低于底线 {threshold}元"
                    self.logger.info(f"商品 {product_data.get('productId')} ({ext_code}) {message}")
                    return True, message
                else:
                    message = "拒绝核价建议失败"
                    self.logger.error(f"商品 {product_data.get('productId')} ({ext_code}) {message}")
                    return False, message
            else:
                # 价格高于底线，同意
                if self.accept_price_review(price_order_id, product_sku_id, suggestion.suggestSupplyPrice):
                    message = f"已同意核价建议，建议价格 {suggestion.suggestSupplyPrice/100}元 高于底线 {threshold}元"
                    self.logger.info(f"商品 {product_data.get('productId')} ({ext_code}) {message}")
                    return True, message
                else:
                    message = "同意核价建议失败"
                    self.logger.error(f"商品 {product_data.get('productId')} ({ext_code}) {message}")
                    return False, message
                    
        except Exception as e:
            error_message = f"处理核价时发生错误: {str(e)}"
            self.logger.error(f"商品 {product_data.get('productId')} ({ext_code}) {error_message}")
            return False, error_message
            
    def batch_process_price_reviews(self, start_page: int = 1, end_page: int = 1, page_size: int = 50) -> List[Dict]:
        """批量处理核价
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
            
        Returns:
            List[Dict]: 处理结果列表，每个结果包含商品ID、处理状态和说明
        """
        results = []
        
        try:
            # 获取待核价商品列表
            products = self.crawl(start_page, end_page, page_size)
            
            # 处理每个商品
            for product in products:
                if self._stop_flag:
                    self.logger.info("批量处理已停止")
                    break
                    
                product_id = product.get('productId')
                self.logger.info(f"正在处理商品 {product_id}")
                
                success, message = self.process_price_review(product)
                
                results.append({
                    'productId': product_id,
                    'success': success,
                    'message': message
                })
                
                # 添加商品之间的延时
                self.random_delay('between_items')
                
            return results
            
        except Exception as e:
            self.logger.error(f"批量处理核价时发生错误: {str(e)}")
            return results 