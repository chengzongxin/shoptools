import json
import time
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
    def __init__(self, cookie: str, mallid: str, logger: logging.Logger, progress_callback=None):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/bg-visage-mms/product/skc/pageQuery"
        
        # 初始化网络请求对象
        self.request = NetworkRequest()
        
        # 保存参数
        self.cookie = cookie
        self.mallid = mallid
        self.logger = logger
        self.progress_callback = progress_callback
        
        # 分页参数
        self.page_size = 20
        self.current_page = 1
        
        # 停止标志
        self._stop_flag = False
        
    def stop(self):
        """停止爬取"""
        self._stop_flag = True
        
    def get_page_data(self, page: int) -> Dict:
        """获取指定页码的数据"""
        payload = {
            "page": page,
            "pageSize": self.page_size
        }
        
        try:
            self.logger.info(f"正在获取第 {page} 页数据")
            self.logger.debug(f"请求URL: {self.api_url}")
            self.logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            result = self.request.post(self.api_url, data=payload)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                return None
                
            return result
            
        except Exception as e:
            self.logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return None
            
    def crawl(self, max_pages: int = 2, page_size: int = 20) -> List[Dict]:
        """爬取商品列表数据"""
        self.page_size = page_size
        all_data = []
        
        for page in range(1, max_pages + 1):
            if self._stop_flag:
                self.logger.info("爬取已停止")
                break
                
            result = self.get_page_data(page)
            
            if not result:
                self.logger.error(f"第 {page} 页数据获取失败")
                break
                
            # 获取商品列表数据
            items = result.get('result', {}).get('pageItems', [])
            if not items:
                self.logger.info("没有更多数据")
                break
                
            all_data.extend(items)
            self.logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            # 更新进度
            if self.progress_callback:
                progress = (page / max_pages) * 100
                self.progress_callback(progress)
            
            time.sleep(1)  # 添加延迟，避免请求过快
            
        return all_data 