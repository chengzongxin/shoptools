import requests
import json
import time
from typing import List, Dict, Any, Optional

class Category:
    def __init__(self, id: str, name: str, level: int, parent_id: str):
        self.id = id
        self.name = name
        self.level = level
        self.parent_id = parent_id

class ProductProperty:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

class SkuSpec:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

class ProductSku:
    def __init__(self, sku_id: str, specs: List[SkuSpec], price: float, stock: int):
        self.sku_id = sku_id
        self.specs = specs
        self.price = price
        self.stock = stock

class Product:
    def __init__(self, product_id: str, title: str, description: str, category: Category,
                 properties: List[ProductProperty], skus: List[ProductSku], images: List[str],
                 status: str, create_time: str, update_time: str):
        self.product_id = product_id
        self.title = title
        self.description = description
        self.category = category
        self.properties = properties
        self.skus = skus
        self.images = images
        self.status = status
        self.create_time = create_time
        self.update_time = update_time

class ProductListCrawler:
    def __init__(self):
        self.base_url = "https://seller-us.temu.com/api/product/list"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": "",
            "Anti-Content": "",
            "MallID": ""
        }
        self.page_size = 20
        
    def set_headers(self, cookie: str, anti_content: str, mallid: str):
        """设置请求头"""
        self.headers["Cookie"] = cookie
        self.headers["Anti-Content"] = anti_content
        self.headers["MallID"] = mallid
        
    def get_page_data(self, page: int) -> List[Product]:
        """获取指定页的数据"""
        try:
            params = {
                "page": page,
                "pageSize": self.page_size,
                "sortField": "create_time",
                "sortOrder": "desc"
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    return self._parse_products(data.get("data", {}).get("list", []))
                else:
                    print(f"API返回错误: {data.get('message')}")
            else:
                print(f"请求失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            
        return []
        
    def get_all_data(self, max_pages: int = 1) -> List[Product]:
        """获取所有页的数据"""
        all_products = []
        page = 1
        
        while page <= max_pages:
            print(f"正在获取第 {page} 页数据...")
            products = self.get_page_data(page)
            
            if not products:
                break
                
            all_products.extend(products)
            print(f"第 {page} 页获取完成，当前共 {len(all_products)} 条数据")
            
            if len(products) < self.page_size:
                break
                
            page += 1
            time.sleep(1)  # 避免请求过快
            
        return all_products
        
    def _parse_products(self, product_list: List[Dict[str, Any]]) -> List[Product]:
        """解析商品数据"""
        products = []
        
        for item in product_list:
            try:
                # 解析分类信息
                category = Category(
                    id=item.get("categoryId", ""),
                    name=item.get("categoryName", ""),
                    level=item.get("categoryLevel", 0),
                    parent_id=item.get("parentCategoryId", "")
                )
                
                # 解析商品属性
                properties = []
                for prop in item.get("properties", []):
                    properties.append(ProductProperty(
                        name=prop.get("name", ""),
                        value=prop.get("value", "")
                    ))
                
                # 解析SKU信息
                skus = []
                for sku in item.get("skus", []):
                    specs = []
                    for spec in sku.get("specs", []):
                        specs.append(SkuSpec(
                            name=spec.get("name", ""),
                            value=spec.get("value", "")
                        ))
                    
                    skus.append(ProductSku(
                        sku_id=sku.get("skuId", ""),
                        specs=specs,
                        price=float(sku.get("price", 0)),
                        stock=int(sku.get("stock", 0))
                    ))
                
                # 创建商品对象
                product = Product(
                    product_id=item.get("productId", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    category=category,
                    properties=properties,
                    skus=skus,
                    images=item.get("images", []),
                    status=item.get("status", ""),
                    create_time=item.get("createTime", ""),
                    update_time=item.get("updateTime", "")
                )
                
                products.append(product)
                
            except Exception as e:
                print(f"解析商品数据时出错: {str(e)}")
                continue
                
        return products 