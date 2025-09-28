"""
竞价管理模块的数据模型
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class TabAggregation:
    """标签聚合信息"""
    count: int
    priceComparingItemTab: int


@dataclass
class TargetProductVO:
    """目标商品信息"""
    productId: int
    name: str
    catNameList: List[str]
    imageList: List[str]
    catIdList: List[int]


@dataclass
class BidOrderItem:
    """竞价订单项"""
    currencyType: str
    currentPriceSort: int
    productId: int
    recommendedPrice: int
    goodsId: int
    confirmInvitingStatus: int
    supplierPrice: Optional[int]
    productCount: int
    type: int
    minPurchaseCount: int
    lowestSupplierPrice: Optional[int]
    skcUnPublishCnt: Optional[int]
    allSkcUnPublish: Optional[bool]
    currentPriceFirst: str
    pdsStatusInfo: Optional[str]
    priceComparingOrderStatus: Optional[int]
    startTime: int
    endTime: int
    priceComparingOrderId: str
    targetProductVO: TargetProductVO
    status: int


@dataclass
class BidOrderListResponse:
    """竞价订单列表响应"""
    tabAggregationList: List[TabAggregation]
    orderItemList: List[BidOrderItem]


@dataclass
class ProductProperty:
    """商品属性"""
    important: bool
    name: str
    value: str


@dataclass
class ProductSku:
    """商品SKU"""
    currencyType: Optional[str]
    comparingCurrencyType: Optional[str]
    productSkuId: int
    propertyValueList: List[str]
    comparingPrice: Optional[int]
    supplierPrice: Optional[int]


@dataclass
class ProductSkc:
    """商品SKC"""
    currencyType: Optional[str]
    comparingCurrencyType: Optional[str]
    result: Optional[str]
    productSkuList: List[ProductSku]
    resultReason: Optional[str]
    unPublishStatus: Optional[int]
    propertyValueList: List[str]
    comparingPrice: Optional[int]
    productSkcId: int
    supplierPrice: Optional[int]
    imageList: List[str]


@dataclass
class CurrentSupplierProduct:
    """当前供应商商品"""
    productId: int
    appealStatus: Optional[int]
    name: str
    productSkcList: List[ProductSkc]
    catNameList: List[str]
    catIdList: List[int]
    imageList: List[str]


@dataclass
class PriceComparingOrderProduct:
    """竞价订单商品"""
    currencyType: str
    productId: int
    name: Optional[str]
    productSkcList: List[ProductSkc]
    catNameList: Optional[List[str]]
    catIdList: Optional[List[int]]
    imageList: List[str]
    productPropertyList: List[ProductProperty]
    currSupplierPrice: str


@dataclass
class BidDetailResponse:
    """竞价详情响应"""
    confirmInvitingStatus: int
    winSupplierPrice: Optional[int]
    apparel: bool
    currentSupplierProduct: CurrentSupplierProduct
    minPurchaseCount: int
    recommendPrice: str
    priceComparingOrderProductSortList: List[PriceComparingOrderProduct]
    sampleToSendStatus: Optional[int]
    currentSupplierPrice: str
    minCurrencyType: str
    endTime: int
    priceComparingOrderId: str
    minSupplierPrice: str
    winCurrencyType: Optional[str]
    targetProduct: CurrentSupplierProduct
    priceComparingOrderProductStatus: int
    comparingProductCount: int


@dataclass
class AdjustSku:
    """价格调整SKU"""
    targetPriceCurrency: str
    oldPriceCurrency: str
    oldSupplyPrice: int
    skuId: int
    targetSupplyPrice: int
    syncPurchasePrice: int


@dataclass
class AdjustItem:
    """价格调整项"""
    productName: str
    productSkcId: int
    productId: int
    skuAdjustList: List[AdjustSku]


@dataclass
class PriceAdjustRequest:
    """价格调整请求"""
    adjustItems: List[AdjustItem]
    adjustReason: int


@dataclass
class BidResult:
    """竞价结果"""
    productId: int
    productName: str
    priceComparingOrderId: str
    originalPrice: float
    bidPrice: float
    minPrice: float
    success: bool
    message: str
    needBid: bool  # 是否需要竞价
