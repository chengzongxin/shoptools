import requests
from typing import Dict, Optional, Any
from ..system_config.config import SystemConfig
from ..logger.logger import Logger

class NetworkRequest:
    """网络请求封装类"""
    
    def __init__(self):
        self.config = SystemConfig()
        self.logger = Logger()
        self.session = requests.Session()
        
    def _get_headers(self, use_compliance: bool = False) -> Dict[str, str]:
        """获取请求头"""
        cookie = self.config.get_compliance_cookie() if use_compliance else self.config.get_seller_cookie()
        mallid = self.config.get_mallid()
        return {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": cookie,
            "mallid": mallid,
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
        
    def get(self, url: str, params: Optional[Dict] = None, use_compliance: bool = False) -> Optional[Dict]:
        """发送GET请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            self.logger.info(f"GET请求成功")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET请求失败: {str(e)}")
            return None
            
    def post(self, url: str, data: Dict[str, Any], use_compliance: bool = False) -> Optional[Dict]:
        """发送POST请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info(f"POST请求成功: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST请求失败: {str(e)}")
            return None
            
    def put(self, url: str, data: Dict[str, Any], use_compliance: bool = False) -> Optional[Dict]:
        """发送PUT请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.put(url, json=data, headers=headers)
            response.raise_for_status()
            self.logger.info(f"PUT请求成功")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT请求失败: {str(e)}")
            return None
            
    def delete(self, url: str, use_compliance: bool = False) -> Optional[Dict]:
        """发送DELETE请求"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.delete(url, headers=headers)
            response.raise_for_status()
            self.logger.info(f"DELETE请求成功")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE请求失败: {str(e)}")
            return None
            
    def download_file(self, url: str, save_path: str, use_compliance: bool = False) -> bool:
        """下载文件"""
        try:
            headers = self._get_headers(use_compliance)
            response = self.session.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"文件下载失败: {str(e)}")
            return False 