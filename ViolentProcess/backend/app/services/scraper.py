"""
爬虫服务模块
实现TEMU和图库网站的接口调用
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class TemuScraper:
    """TEMU网站爬虫类"""
    
    def __init__(self):
        self.base_url = "https://www.temu.com"
        self.session = requests.Session()
        self.cookie = os.getenv("TEMU_COOKIE", "")
        self._setup_session()
    
    def _setup_session(self):
        """设置会话配置"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        
        if self.cookie:
            self.session.headers.update({"Cookie": self.cookie})
    
    def search_products(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索TEMU商品"""
        try:
            search_url = f"{self.base_url}/api/search"
            params = {"q": keyword, "limit": limit, "page": 1}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            if "data" in data and "items" in data["data"]:
                for item in data["data"]["items"]:
                    product = {
                        "id": item.get("id", ""),
                        "title": item.get("title", ""),
                        "price": item.get("price", ""),
                        "image_url": item.get("image", ""),
                        "spuid": item.get("spuid", ""),
                        "status": item.get("status", "active")
                    }
                    products.append(product)
            
            return products
            
        except Exception as e:
            print(f"TEMU搜索异常: {e}")
            return []
    
    def off_shelf_product(self, product_id: str) -> bool:
        """下架商品"""
        try:
            off_shelf_url = f"{self.base_url}/api/product/off-shelf"
            data = {"product_id": product_id, "reason": "违规处理"}
            
            response = self.session.post(off_shelf_url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get("success", False)
            
        except Exception as e:
            print(f"下架商品失败: {e}")
            return False

class BlueSiteScraper:
    """蓝色图库网站爬虫类"""
    
    def __init__(self):
        self.base_url = "https://www.blueimagesite.com"
        self.session = requests.Session()
        self.cookie = os.getenv("BLUE_COOKIE", "")
        self._setup_session()
    
    def _setup_session(self):
        """设置会话配置"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        
        if self.cookie:
            self.session.headers.update({"Cookie": self.cookie})
    
    def search_images(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索图库图片"""
        try:
            search_url = f"{self.base_url}/search"
            params = {"q": keyword, "limit": limit, "page": 1}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = []
            
            image_elements = soup.select(".image-item, .search-result, .gallery-item")
            
            for element in image_elements[:limit]:
                image = {
                    "id": element.get("data-id", ""),
                    "title": element.get("alt", ""),
                    "image_url": element.get("src", ""),
                    "thumbnail_url": element.get("data-thumb", ""),
                    "file_size": element.get("data-size", ""),
                    "upload_date": element.get("data-date", "")
                }
                images.append(image)
            
            return images
            
        except Exception as e:
            print(f"图库搜索异常: {e}")
            return []
    
    def delete_image(self, image_id: str) -> bool:
        """删除图片"""
        try:
            delete_url = f"{self.base_url}/api/image/delete"
            data = {"image_id": image_id, "reason": "违规处理"}
            
            response = self.session.post(delete_url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get("success", False)
            
        except Exception as e:
            print(f"删除图片失败: {e}")
            return False

# 全局爬虫实例
temu_scraper = TemuScraper()
blue_scraper = BlueSiteScraper()

def search_temu_products(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """搜索TEMU商品的便捷函数"""
    return temu_scraper.search_products(keyword, limit)

def search_blue_images(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """搜索图库图片的便捷函数"""
    return blue_scraper.search_images(keyword, limit)

def off_shelf_temu_product(product_id: str) -> bool:
    """下架TEMU商品的便捷函数"""
    return temu_scraper.off_shelf_product(product_id)

def delete_blue_image(image_id: str) -> bool:
    """删除图库图片的便捷函数"""
    return blue_scraper.delete_image(image_id) 