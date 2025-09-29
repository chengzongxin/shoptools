"""
竞价管理核心业务逻辑
"""
import json
import time
import random
import logging
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal, ROUND_DOWN
from ..network.request import NetworkRequest
from src.config.config import category_config, bid_config
from .models import (
    BidOrderListResponse, BidOrderItem, BidDetailResponse, 
    BidResult, AdjustItem, AdjustSku, PriceAdjustRequest,
    TabAggregation, TargetProductVO, CurrentSupplierProduct,
    ProductSkc, ProductSku, PriceComparingOrderProduct
)


class BidManagementCrawler:
    """竞价管理爬虫类"""
    
    def __init__(self, logger: logging.Logger = None, progress_callback=None):
        self.logger = logger or logging.getLogger(__name__)
        self.progress_callback = progress_callback
        self.request = NetworkRequest()
        self.base_url = "https://agentseller.temu.com/api/kiana"
        
        # API端点
        self.search_url = f"{self.base_url}/zoro/PriceComparingOrderSupplierRpcService/searchForSupplier"
        self.detail_url = f"{self.base_url}/zoro/PriceComparingOrderSupplierRpcService/queryPriceComparingOrderDetail"
        self.confirm_url = f"{self.base_url}/zoro/PriceComparingOrderSupplierRpcService/confirmInvitation"
        self.price_adjust_url = f"{self.base_url}/mms/gmp/bg/magneto/api/price/priceAdjust/gmpProductBatchAdjustPrice"
        
        # 从配置文件加载竞价配置
        self.bid_reduction = bid_config.get_bid_reduction()
        self.max_page_size = bid_config.get_max_page_size()
        self.enable_price_threshold_check = bid_config.is_price_threshold_check_enabled()
        
        # 获取随机延时配置
        self.delay_min, self.delay_max = bid_config.get_random_delay_range()
        
    def random_delay(self, min_sec: float = None, max_sec: float = None):
        """随机延时"""
        if min_sec is None:
            min_sec = self.delay_min
        if max_sec is None:
            max_sec = self.delay_max
        delay = random.uniform(min_sec, max_sec)
        self.logger.info(f"随机延时 {delay:.2f} 秒")
        time.sleep(delay)
        
    def update_progress(self, message: str, current: int = None, total: int = None):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        self.logger.info(message)
    
    def get_pending_invitations(self, page: int = 1, page_size: int = 10) -> Optional[BidOrderListResponse]:
        """获取待确认邀约列表"""
        self.random_delay()
        
        data = {
            "pageSize": page_size,
            "page": page,
            "status": 2,
            "confirmInvitingStatus": 0
        }
        
        self.logger.info(f"获取待确认邀约列表，页码: {page}, 页大小: {page_size}")
        response = self.request.post(self.search_url, data)
        
        if not response or not response.get("success"):
            self.logger.error(f"获取待确认邀约失败: {response}")
            return None
            
        result = response.get("result", {})
        return self._parse_order_list_response(result)
    
    def get_failed_bids(self, page: int = 1, page_size: int = 10) -> Optional[BidOrderListResponse]:
        """获取竞价失败列表"""
        self.random_delay()
        
        data = {
            "pageSize": page_size,
            "page": page,
            "status": 5
        }
        
        self.logger.info(f"获取竞价失败列表，页码: {page}, 页大小: {page_size}")
        response = self.request.post(self.search_url, data)
        
        if not response or not response.get("success"):
            self.logger.error(f"获取竞价失败列表失败: {response}")
            return None
            
        result = response.get("result", {})
        return self._parse_order_list_response(result)
    
    def get_all_pending_and_failed_items(self) -> List[BidOrderItem]:
        """获取所有待处理的竞价商品"""
        all_items = []
        
        # 先获取第一页来确定总数
        self.update_progress("获取待确认邀约数据...")
        pending_response = self.get_pending_invitations(page=1, page_size=self.max_page_size)
        
        if pending_response:
            # 计算待确认邀约的总页数
            pending_count = 0
            for tab in pending_response.tabAggregationList:
                if tab.priceComparingItemTab == 1:  # 待邀约
                    pending_count = tab.count
                    break
            
            self.logger.info(f"待确认邀约总数: {pending_count}")
            
            # 获取所有待确认邀约页面
            pending_pages = (pending_count + self.max_page_size - 1) // self.max_page_size
            for page in range(1, pending_pages + 1):
                self.update_progress(f"获取待确认邀约第 {page}/{pending_pages} 页")
                if page == 1:
                    response = pending_response
                else:
                    response = self.get_pending_invitations(page, self.max_page_size)
                
                if response and response.orderItemList:
                    all_items.extend(response.orderItemList)
        
        # 获取竞价失败列表
        self.update_progress("获取竞价失败数据...")
        failed_response = self.get_failed_bids(page=1, page_size=self.max_page_size)
        
        if failed_response:
            # 计算竞价失败的总数
            failed_count = 0
            for tab in failed_response.tabAggregationList:
                if tab.priceComparingItemTab == 5:  # 竞价失败
                    failed_count = tab.count
                    break
            
            self.logger.info(f"竞价失败总数: {failed_count}")
            
            # 获取所有竞价失败页面
            failed_pages = (failed_count + self.max_page_size - 1) // self.max_page_size
            for page in range(1, failed_pages + 1):
                self.update_progress(f"获取竞价失败第 {page}/{failed_pages} 页")
                if page == 1:
                    response = failed_response
                else:
                    response = self.get_failed_bids(page, self.max_page_size)
                
                if response and response.orderItemList:
                    all_items.extend(response.orderItemList)
        
        self.logger.info(f"总共获取到 {len(all_items)} 个待处理商品")
        return all_items
    
    def get_bid_detail(self, product_id: int, price_comparing_order_id: str) -> Optional[BidDetailResponse]:
        """获取竞价详情"""
        self.random_delay()
        
        data = {
            "productId": product_id,
            "priceComparingOrderId": price_comparing_order_id
        }
        
        self.logger.info(f"获取竞价详情，商品ID: {product_id}, 订单ID: {price_comparing_order_id}")
        response = self.request.post(self.detail_url, data)
        
        if not response or not response.get("success"):
            self.logger.error(f"获取竞价详情失败: {response}")
            return None
            
        result = response.get("result", {})
        return self._parse_bid_detail_response(result)
    
    def confirm_invitation(self, product_id: int, price_comparing_order_id: str) -> bool:
        """确认邀约"""
        self.random_delay()
        
        data = {
            "productId": product_id,
            "priceComparingOrderId": price_comparing_order_id
        }
        
        self.logger.info(f"确认邀约，商品ID: {product_id}, 订单ID: {price_comparing_order_id}")
        response = self.request.post(self.confirm_url, data)
        
        if not response or not response.get("success"):
            self.logger.error(f"确认邀约失败: {response}")
            return False
            
        self.logger.info("确认邀约成功")
        return True
    
    def adjust_price(self, adjust_request: PriceAdjustRequest) -> bool:
        """调整价格"""
        self.random_delay()
        
        data = {
            "adjustItems": [
                {
                    "productName": item.productName,
                    "productSkcId": item.productSkcId,
                    "productId": item.productId,
                    "skuAdjustList": [
                        {
                            "targetPriceCurrency": sku.targetPriceCurrency,
                            "oldPriceCurrency": sku.oldPriceCurrency,
                            "oldSupplyPrice": sku.oldSupplyPrice,
                            "skuId": sku.skuId,
                            "targetSupplyPrice": sku.targetSupplyPrice,
                            "syncPurchasePrice": sku.syncPurchasePrice
                        } for sku in item.skuAdjustList
                    ]
                } for item in adjust_request.adjustItems
            ],
            "adjustReason": adjust_request.adjustReason
        }
        
        self.logger.info(f"调整价格，请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        response = self.request.post(self.price_adjust_url, data)
        
        if not response or not response.get("success"):
            self.logger.error(f"调整价格失败: {response}")
            return False
            
        self.logger.info("调整价格成功")
        return True
    
    def calculate_bid_price(self, current_price: float, min_price: float, category_ids: List[int] = None) -> Tuple[float, bool, str]:
        """计算竞价价格
        
        Args:
            current_price: 当前价格
            min_price: 最低价格
            category_ids: 商品类别ID列表
        
        Returns:
            tuple: (bid_price, need_bid, reason)
        """
        # 如果当前价格已经是最低价，不需要竞价
        if abs(current_price - min_price) < 0.01:
            return current_price, False, "当前价格已是最低价"
        
        # 计算竞价价格：比最低价减少设定的金额
        bid_price = min_price - self.bid_reduction
        
        # 检查价格底线（如果启用了价格阈值检查）
        if self.enable_price_threshold_check and category_ids:
            price_threshold = category_config.get_price_threshold_by_category_ids(category_ids)
            if price_threshold is not None:
                self.logger.info(f"商品类别价格阈值: {price_threshold}")
                
                # 如果竞价价格低于价格阈值，不参与竞价
                if bid_price < price_threshold:
                    reason = f"竞价价格({bid_price})低于类别价格阈值({price_threshold})，不参与竞价"
                    self.logger.warning(reason)
                    return current_price, False, reason
                
                # 如果最低价已经低于价格阈值，也不参与竞价
                if min_price < price_threshold:
                    reason = f"最低价({min_price})已低于类别价格阈值({price_threshold})，不参与竞价"
                    self.logger.warning(reason)
                    return current_price, False, reason
            else:
                self.logger.info(f"未找到类别ID {category_ids} 的价格阈值配置")
        
        # 确保竞价价格不会过低（至少0.01元）
        if bid_price < 0.01:
            bid_price = 0.01
        
        # 保留两位小数
        bid_price = float(Decimal(str(bid_price)).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        
        self.logger.info(f"价格计算: 最低价={min_price}, 减价金额={self.bid_reduction}, 竞价价格={bid_price}")
        
        return bid_price, True, "可以竞价"
    
    def process_single_bid(self, item: BidOrderItem) -> BidResult:
        """处理单个商品竞价"""
        product_id = item.productId
        product_name = item.targetProductVO.name
        order_id = item.priceComparingOrderId
        
        self.logger.info(f"开始处理商品竞价: {product_name} (ID: {product_id})")
        
        # 获取竞价详情
        detail = self.get_bid_detail(product_id, order_id)
        if not detail:
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=0,
                bidPrice=0,
                minPrice=0,
                success=False,
                message="获取竞价详情失败",
                needBid=False
            )
        
        # 解析价格信息
        try:
            # 去掉货币符号和单位，提取数字
            current_price_str = detail.currentSupplierPrice.replace("¥", "").replace(" ", "").replace("CNY", "")
            min_price_str = detail.minSupplierPrice
            
            current_price = float(current_price_str)
            min_price = float(min_price_str)
            
            self.logger.info(f"当前价格: {current_price}, 最低价格: {min_price}")
            
        except (ValueError, AttributeError) as e:
            self.logger.error(f"解析价格失败: {e}")
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=0,
                bidPrice=0,
                minPrice=0,
                success=False,
                message=f"解析价格失败: {e}",
                needBid=False
            )
        
        # 计算竞价价格（传入商品类别信息用于价格阈值检查）
        category_ids = item.targetProductVO.catIdList if item.targetProductVO else []
        bid_price, need_bid, reason = self.calculate_bid_price(current_price, min_price, category_ids)
        
        if not need_bid:
            self.logger.info(f"商品 {product_name}: {reason}")
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=current_price,
                bidPrice=current_price,
                minPrice=min_price,
                success=True,
                message=reason,
                needBid=False
            )
        
        self.logger.info(f"计算竞价价格: {bid_price}")
        
        # 确认邀约
        if not self.confirm_invitation(product_id, order_id):
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=current_price,
                bidPrice=bid_price,
                minPrice=min_price,
                success=False,
                message="确认邀约失败",
                needBid=True
            )
        
        # 构造价格调整请求
        try:
            # 从详情中获取SKU信息进行价格调整
            adjust_items = []
            
            for product_sort in detail.priceComparingOrderProductSortList:
                if product_sort.productId == product_id:
                    for skc in product_sort.productSkcList:
                        sku_adjust_list = []
                        for sku in skc.productSkuList:
                            # 将价格从元转换为分
                            old_price_cents = int(current_price * 100)
                            new_price_cents = int(bid_price * 100)
                            
                            adjust_sku = AdjustSku(
                                targetPriceCurrency="CNY",
                                oldPriceCurrency="CNY",
                                oldSupplyPrice=old_price_cents,
                                skuId=sku.productSkuId,
                                targetSupplyPrice=new_price_cents,
                                syncPurchasePrice=1
                            )
                            sku_adjust_list.append(adjust_sku)
                        
                        adjust_item = AdjustItem(
                            productName=product_name,
                            productSkcId=skc.productSkcId,
                            productId=product_id,
                            skuAdjustList=sku_adjust_list
                        )
                        adjust_items.append(adjust_item)
                    break
            
            if not adjust_items:
                return BidResult(
                    productId=product_id,
                    productName=product_name,
                    priceComparingOrderId=order_id,
                    originalPrice=current_price,
                    bidPrice=bid_price,
                    minPrice=min_price,
                    success=False,
                    message="未找到可调整的SKU信息",
                    needBid=True
                )
            
            # 调整价格
            adjust_request = PriceAdjustRequest(
                adjustItems=adjust_items,
                adjustReason=bid_config.get_adjust_reason()  # 从配置获取调整原因
            )
            
            if not self.adjust_price(adjust_request):
                return BidResult(
                    productId=product_id,
                    productName=product_name,
                    priceComparingOrderId=order_id,
                    originalPrice=current_price,
                    bidPrice=bid_price,
                    minPrice=min_price,
                    success=False,
                    message="价格调整失败",
                    needBid=True
                )
            
            self.logger.info(f"商品 {product_name} 竞价成功，价格从 {current_price} 调整为 {bid_price}")
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=current_price,
                bidPrice=bid_price,
                minPrice=min_price,
                success=True,
                message="竞价成功",
                needBid=True
            )
            
        except Exception as e:
            self.logger.error(f"处理价格调整时发生异常: {e}")
            return BidResult(
                productId=product_id,
                productName=product_name,
                priceComparingOrderId=order_id,
                originalPrice=current_price,
                bidPrice=bid_price,
                minPrice=min_price,
                success=False,
                message=f"处理异常: {e}",
                needBid=True
            )
    
    def process_all_bids(self) -> List[BidResult]:
        """处理所有竞价"""
        self.update_progress("开始获取待处理商品...")
        
        # 获取所有待处理商品
        items = self.get_all_pending_and_failed_items()
        if not items:
            self.logger.warning("没有找到待处理的竞价商品")
            return []
        
        self.logger.info(f"开始处理 {len(items)} 个商品的竞价")
        results = []
        
        for i, item in enumerate(items, 1):
            self.update_progress(f"处理第 {i}/{len(items)} 个商品竞价", i, len(items))
            
            try:
                result = self.process_single_bid(item)
                results.append(result)
                
                # 记录结果
                if result.success:
                    if result.needBid:
                        self.logger.info(f"✅ {result.productName}: 竞价成功 ({result.originalPrice} -> {result.bidPrice})")
                    else:
                        self.logger.info(f"ℹ️ {result.productName}: {result.message}")
                else:
                    self.logger.error(f"❌ {result.productName}: {result.message}")
                    
            except Exception as e:
                self.logger.error(f"处理商品 {item.targetProductVO.name} 时发生异常: {e}")
                results.append(BidResult(
                    productId=item.productId,
                    productName=item.targetProductVO.name,
                    priceComparingOrderId=item.priceComparingOrderId,
                    originalPrice=0,
                    bidPrice=0,
                    minPrice=0,
                    success=False,
                    message=f"处理异常: {e}",
                    needBid=False
                ))
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        bid_count = sum(1 for r in results if r.needBid and r.success)
        no_bid_count = sum(1 for r in results if not r.needBid and r.success)
        
        self.update_progress(f"竞价处理完成！成功: {success_count}, 实际竞价: {bid_count}, 无需竞价: {no_bid_count}")
        
        return results
    
    def _parse_order_list_response(self, result: Dict[str, Any]) -> BidOrderListResponse:
        """解析订单列表响应"""
        tab_aggregations = []
        for tab_data in result.get("tabAggregationList", []):
            tab_aggregations.append(TabAggregation(
                count=tab_data.get("count", 0),
                priceComparingItemTab=tab_data.get("priceComparingItemTab", 0)
            ))
        
        order_items = []
        for item_data in result.get("orderItemList", []):
            target_product_data = item_data.get("targetProductVO", {})
            target_product = TargetProductVO(
                productId=target_product_data.get("productId", 0),
                name=target_product_data.get("name", ""),
                catNameList=target_product_data.get("catNameList", []),
                imageList=target_product_data.get("imageList", []),
                catIdList=target_product_data.get("catIdList", [])
            )
            
            order_item = BidOrderItem(
                currencyType=item_data.get("currencyType", ""),
                currentPriceSort=item_data.get("currentPriceSort", 0),
                productId=item_data.get("productId", 0),
                recommendedPrice=item_data.get("recommendedPrice", 0),
                goodsId=item_data.get("goodsId", 0),
                confirmInvitingStatus=item_data.get("confirmInvitingStatus", 0),
                supplierPrice=item_data.get("supplierPrice"),
                productCount=item_data.get("productCount", 0),
                type=item_data.get("type", 0),
                minPurchaseCount=item_data.get("minPurchaseCount", 0),
                lowestSupplierPrice=item_data.get("lowestSupplierPrice"),
                skcUnPublishCnt=item_data.get("skcUnPublishCnt"),
                allSkcUnPublish=item_data.get("allSkcUnPublish"),
                currentPriceFirst=item_data.get("currentPriceFirst", ""),
                pdsStatusInfo=item_data.get("pdsStatusInfo"),
                priceComparingOrderStatus=item_data.get("priceComparingOrderStatus"),
                startTime=item_data.get("startTime", 0),
                endTime=item_data.get("endTime", 0),
                priceComparingOrderId=item_data.get("priceComparingOrderId", ""),
                targetProductVO=target_product,
                status=item_data.get("status", 0)
            )
            order_items.append(order_item)
        
        return BidOrderListResponse(
            tabAggregationList=tab_aggregations,
            orderItemList=order_items
        )
    
    def _parse_bid_detail_response(self, result: Dict[str, Any]) -> BidDetailResponse:
        """解析竞价详情响应"""
        # 解析当前供应商商品
        current_supplier_data = result.get("currentSupplierProduct", {})
        current_supplier_product = self._parse_supplier_product(current_supplier_data)
        
        # 解析目标商品
        target_product_data = result.get("targetProduct", {})
        target_product = self._parse_supplier_product(target_product_data)
        
        # 解析竞价订单商品排序列表
        sort_list = []
        for sort_data in result.get("priceComparingOrderProductSortList", []):
            sort_product = self._parse_price_comparing_order_product(sort_data)
            sort_list.append(sort_product)
        
        return BidDetailResponse(
            confirmInvitingStatus=result.get("confirmInvitingStatus", 0),
            winSupplierPrice=result.get("winSupplierPrice"),
            apparel=result.get("apparel", False),
            currentSupplierProduct=current_supplier_product,
            minPurchaseCount=result.get("minPurchaseCount", 0),
            recommendPrice=result.get("recommendPrice", ""),
            priceComparingOrderProductSortList=sort_list,
            sampleToSendStatus=result.get("sampleToSendStatus"),
            currentSupplierPrice=result.get("currentSupplierPrice", ""),
            minCurrencyType=result.get("minCurrencyType", ""),
            endTime=result.get("endTime", 0),
            priceComparingOrderId=result.get("priceComparingOrderId", ""),
            minSupplierPrice=result.get("minSupplierPrice", ""),
            winCurrencyType=result.get("winCurrencyType"),
            targetProduct=target_product,
            priceComparingOrderProductStatus=result.get("priceComparingOrderProductStatus", 0),
            comparingProductCount=result.get("comparingProductCount", 0)
        )
    
    def _parse_supplier_product(self, data: Dict[str, Any]) -> CurrentSupplierProduct:
        """解析供应商商品数据"""
        skc_list = []
        for skc_data in data.get("productSkcList", []):
            sku_list = []
            for sku_data in skc_data.get("productSkuList", []):
                sku = ProductSku(
                    currencyType=sku_data.get("currencyType"),
                    comparingCurrencyType=sku_data.get("comparingCurrencyType"),
                    productSkuId=sku_data.get("productSkuId", 0),
                    propertyValueList=sku_data.get("propertyValueList", []),
                    comparingPrice=sku_data.get("comparingPrice"),
                    supplierPrice=sku_data.get("supplierPrice")
                )
                sku_list.append(sku)
            
            skc = ProductSkc(
                currencyType=skc_data.get("currencyType"),
                comparingCurrencyType=skc_data.get("comparingCurrencyType"),
                result=skc_data.get("result"),
                productSkuList=sku_list,
                resultReason=skc_data.get("resultReason"),
                unPublishStatus=skc_data.get("unPublishStatus"),
                propertyValueList=skc_data.get("propertyValueList", []),
                comparingPrice=skc_data.get("comparingPrice"),
                productSkcId=skc_data.get("productSkcId", 0),
                supplierPrice=skc_data.get("supplierPrice"),
                imageList=skc_data.get("imageList", [])
            )
            skc_list.append(skc)
        
        return CurrentSupplierProduct(
            productId=data.get("productId", 0),
            appealStatus=data.get("appealStatus"),
            name=data.get("name", ""),
            productSkcList=skc_list,
            catNameList=data.get("catNameList", []),
            catIdList=data.get("catIdList", []),
            imageList=data.get("imageList", [])
        )
    
    def _parse_price_comparing_order_product(self, data: Dict[str, Any]) -> PriceComparingOrderProduct:
        """解析竞价订单商品数据"""
        from .models import ProductProperty
        
        skc_list = []
        for skc_data in data.get("productSkcList", []):
            sku_list = []
            for sku_data in skc_data.get("productSkuList", []):
                sku = ProductSku(
                    currencyType=sku_data.get("currencyType"),
                    comparingCurrencyType=sku_data.get("comparingCurrencyType"),
                    productSkuId=sku_data.get("productSkuId", 0),
                    propertyValueList=sku_data.get("propertyValueList", []),
                    comparingPrice=sku_data.get("comparingPrice"),
                    supplierPrice=sku_data.get("supplierPrice")
                )
                sku_list.append(sku)
            
            skc = ProductSkc(
                currencyType=skc_data.get("currencyType"),
                comparingCurrencyType=skc_data.get("comparingCurrencyType"),
                result=skc_data.get("result"),
                productSkuList=sku_list,
                resultReason=skc_data.get("resultReason"),
                unPublishStatus=skc_data.get("unPublishStatus"),
                propertyValueList=skc_data.get("propertyValueList", []),
                comparingPrice=skc_data.get("comparingPrice"),
                productSkcId=skc_data.get("productSkcId", 0),
                supplierPrice=skc_data.get("supplierPrice"),
                imageList=skc_data.get("imageList", [])
            )
            skc_list.append(skc)
        
        # 解析商品属性
        property_list = []
        for prop_data in data.get("productPropertyList", []):
            prop = ProductProperty(
                important=prop_data.get("important", False),
                name=prop_data.get("name", ""),
                value=prop_data.get("value", "")
            )
            property_list.append(prop)
        
        return PriceComparingOrderProduct(
            currencyType=data.get("currencyType", ""),
            productId=data.get("productId", 0),
            name=data.get("name"),
            productSkcList=skc_list,
            catNameList=data.get("catNameList"),
            catIdList=data.get("catIdList"),
            imageList=data.get("imageList", []),
            productPropertyList=property_list,
            currSupplierPrice=data.get("currSupplierPrice", "")
        )
