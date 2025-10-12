import json
import os
import sys
import browsercookie
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

class SystemConfig:
    """系统配置管理类"""
    
    _instance: Optional['SystemConfig'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """初始化配置"""
        # 处理打包环境和开发环境的路径差异
        if getattr(sys, 'frozen', False):
            # 打包环境：从可执行文件目录查找配置
            base_path = sys._MEIPASS
            self.config_file = os.path.join(base_path, 'config', 'system_config.json')
        else:
            # 开发环境：从源码目录查找配置
            self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'system_config.json')
        self.config: Dict = self._load_config()
        
        # 统一使用agentseller.temu.com域名
        self.base_url = "https://agentseller.temu.com"
        
        # 定义测试API
        self.test_api_url = "https://agentseller.temu.com/api/seller/auth/userInfo"
        
        # 延迟初始化网络请求实例，避免循环导入
        self._request = None
        
    def _get_request(self):
        """延迟获取NetworkRequest实例，避免循环导入"""
        if self._request is None:
            from ..network.request import NetworkRequest
            self._request = NetworkRequest()
        return self._request
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            # 如果配置文件不存在,创建默认配置
            default_config = {
                "cookie": "",
                "mallid": "",
                "last_update": ""
            }
            self._save_config(default_config)
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 兼容旧版本配置，迁移数据
                if "seller_cookie" in config or "compliance_cookie" in config:
                    # 优先使用seller_cookie，如果没有则使用compliance_cookie
                    cookie = config.get("seller_cookie") or config.get("compliance_cookie", "")
                    new_config = {
                        "cookie": cookie,
                        "mallid": config.get("mallid", ""),
                        "last_update": config.get("last_update", "")
                    }
                    self._save_config(new_config)
                    return new_config
                return config
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return {}
            
    def _save_config(self, config: Dict) -> None:
        """保存配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
    
    def get_website_cookies(self, website_url: str) -> Tuple[str, str]:
        """
        获取特定网站的cookie
        
        参数:
            website_url: 网站URL
            
        返回:
            tuple: (cookie_string, error_message)
        """
        try:
            # 获取Chrome浏览器的所有cookie
            all_cookies = browsercookie.chrome()
            
            # 解析URL以获取域名
            parsed_url = urlparse(website_url)
            domain = parsed_url.netloc
            
            # 过滤出特定网站的cookie
            website_cookies = {}
            
            for cookie in all_cookies:
                # 检查cookie是否属于目标网站
                if domain in cookie.domain or cookie.domain.lstrip('.') in domain:
                    website_cookies[cookie.name] = cookie.value
            
            if not website_cookies:
                return "", f"未找到 {domain} 的Cookie，请确保已在浏览器中登录该网站"
            
            # 转换为F12格式的字符串
            cookie_string = "; ".join([f"{name}={value}" for name, value in website_cookies.items()])
            return cookie_string, ""
            
        except Exception as e:
            return "", f"获取Cookie失败: {str(e)}"
    
    def get_cookie_from_browser(self) -> Tuple[str, str]:
        """从浏览器获取agentseller.temu.com的Cookie"""
        return self.get_website_cookies(self.base_url)
    
    def get_cookie_from_websocket(self) -> Tuple[str, str]:
        """通过WebSocket从Chrome插件获取Cookie"""
        try:
            from .websocket_cookie import get_websocket_manager
            manager = get_websocket_manager()
            return manager.get_domain_cookies(self.base_url)
        except ImportError:
            return "", "WebSocket模块未安装，请安装websockets依赖"
        except Exception as e:
            return "", f"WebSocket获取Cookie失败: {str(e)}"
    
    def test_api(self, cookie: str = None) -> Tuple[bool, str, Dict]:
        """
        测试API连接
        
        参数:
            cookie: 要测试的cookie，如果为None则使用配置中的cookie
            
        返回:
            tuple: (success, message, result_data)
        """
        if cookie is None:
            cookie = self.get_cookie()
        
        if not cookie:
            return False, "Cookie为空，请先获取或配置Cookie", {}
        
        try:
            # 获取NetworkRequest实例
            request = self._get_request()
            
            # 临时更新配置中的cookie以便使用NetworkRequest
            original_cookie = self.config.get("cookie", "")
            self.config["cookie"] = cookie
            
            # 使用NetworkRequest发送POST请求
            result = request.post(self.test_api_url, data={})
            
            # 恢复原始cookie
            self.config["cookie"] = original_cookie
            
            if not result:
                return False, "API请求失败，请检查Cookie是否有效", {}
            
            if result.get('success'):
                user_info = result.get('result', {})
                mall_info = ""
                if user_info.get('mallList'):
                    for mall in user_info['mallList']:
                        mall_name = mall.get('mallName', 'N/A')
                        mall_id = mall.get('mallId', 'N/A')
                        managed_type = mall.get('managedType', 'N/A')
                        mall_info += f"店铺: {mall_name} (ID: {mall_id}, 管理类型: {managed_type})\n"
                
                message = f"✅ API测试成功！\n"
                message += f"账户ID: {user_info.get('accountId', 'N/A')}\n"
                message += f"手机号: {user_info.get('maskMobile', 'N/A')}\n"
                message += f"账户类型: {user_info.get('accountType', 'N/A')}\n"
                message += f"{mall_info}"
                
                return True, message, result
            else:
                return False, f"API返回失败: {result.get('errorMsg', '未知错误')}", result
                
        except Exception as e:
            return False, f"测试失败: {str(e)}", {}
            
    def get_cookie(self) -> str:
        """获取cookie"""
        return self.config.get("cookie", "")
        
    def get_mallid(self) -> str:
        """获取mallid"""
        return self.config.get("mallid", "")
        
    def update_config(self, cookie: str = "", mallid: str = "") -> None:
        """更新配置"""
        self.config["cookie"] = cookie
        self.config["mallid"] = mallid
            
        self.config["last_update"] = self._get_current_time()
        self._save_config(self.config)
        
    # 保留兼容性方法，避免其他模块调用报错
    def get_seller_cookie(self) -> str:
        """获取cookie（兼容性方法）"""
        return self.get_cookie()
        
    def get_compliance_cookie(self) -> str:
        """获取cookie（兼容性方法）"""
        return self.get_cookie()
        
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 