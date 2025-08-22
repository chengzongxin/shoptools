import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from ..network.request import NetworkRequest

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Category:
    catId: int
    catName: str
    catEnName: Optional[str]
    catType: Optional[int]

@dataclass
class ProductProperty:
    templatePid: int
    pid: int
    refPid: int
    propName: str
    vid: int
    propValue: str
    valueUnit: str
    valueExtendInfo: str
    numberInputValue: str

@dataclass
class SkuSpec:
    parentSpecId: int
    parentSpecName: str
    specId: int
    specName: str
    unitSpecName: Optional[str]

@dataclass
class ProductSku:
    productSkuId: int
    thumbUrl: str
    productSkuSpecList: List[SkuSpec]
    extCode: str
    supplierPrice: int

@dataclass
class Product:
    productId: int
    productSkcId: int
    productName: str
    productType: int
    sourceType: int
    goodsId: int
    leafCat: Category
    categories: Dict[str, Category]
    productProperties: List[ProductProperty]
    mainImageUrl: str
    productSkuSummaries: List[ProductSku]
    createdAt: datetime

class ProductListCrawler:
    def __init__(self, logger=None):
        self.api_url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
        self.page_size = 20
        self.current_page = 1
        self.request = NetworkRequest()
        self.logger = logger or logging.getLogger('product_list')

    def get_page_data(self, page: int, page_size: int = None, only_on_sale: bool = False) -> Optional[Dict]:
        """获取指定页码的数据"""
        payload = {
            "page": page,
            "pageSize": page_size or self.page_size
        }
        
        # 如果选择只爬取在售商品，添加 skcTopStatus 参数
        if only_on_sale:
            payload["skcTopStatus"] = 100
            self.logger.debug(f"添加在售商品筛选参数: skcTopStatus=100")
        
        self.logger.info(f"正在获取第 {page} 页数据")
        self.logger.debug(f"请求URL: {self.api_url}")
        self.logger.debug(f"请求体: {payload}")
        result = self.request.post(self.api_url, data=payload)
        if not result or not result.get('success', True):
            self.logger.error(f"第 {page} 页数据获取失败: {result}")
            return None
        return result

    def get_all_data(self, max_pages: int = 2, page_size: int = None, only_on_sale: bool = False) -> List[Dict]:
        """获取指定页数的数据"""
        all_data = []
        for page in range(1, max_pages + 1):
            result = self.get_page_data(page, page_size, only_on_sale)
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                break
            items = result.get('result', {}).get('pageItems', [])
            if not items:
                self.logger.info("没有更多数据")
                break
            all_data.extend(items)
            self.logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
        return all_data 