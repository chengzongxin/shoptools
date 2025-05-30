import requests
import json
import time
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

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
    def __init__(self):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/bg-visage-mms/product/skc/pageQuery"
        
        # 请求头
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": "",
            "mallid": "",
            "origin": "https://seller.kuajingmaihuo.com",
            "referer": "https://seller.kuajingmaihuo.com/goods/product/list",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
        }
        
        # 分页参数
        self.page_size = 20
        self.current_page = 1
        
    def get_page_data(self, page: int) -> Dict:
        """获取指定页码的数据"""
        payload = {
            "page": page,
            "pageSize": self.page_size
        }
        
        try:
            logger.info(f"正在获取第 {page} 页数据")
            logger.debug(f"请求URL: {self.api_url}")
            logger.debug(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return None
                
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            logger.error(f"响应内容: {response.text}")
            return None
        except Exception as e:
            logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return None
            
    def get_all_data(self, max_pages: int = 2) -> List[Dict]:
        """获取指定页数的数据"""
        all_data = []
        
        for page in range(1, max_pages + 1):
            result = self.get_page_data(page)
            
            if not result:
                logger.error(f"第 {page} 页数据获取失败")
                break
                
            # 获取商品列表数据
            items = result.get('result', {}).get('pageItems', [])
            if not items:
                logger.info("没有更多数据")
                break
                
            all_data.extend(items)
            logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            time.sleep(1)  # 添加延迟，避免请求过快
            
        return all_data 