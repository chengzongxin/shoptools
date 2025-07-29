import json
import os
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
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'system_config.json')
        self.config: Dict = self._load_config()
        
        # 定义网站URL
        self.seller_url = "https://seller.kuajingmaihuo.com"
        self.compliance_url = "https://agentseller.temu.com"
        
        # 定义测试API
        self.seller_test_api = "https://seller.kuajingmaihuo.com/bg/quiet/api/mms/userInfo"
        self.compliance_test_api = "https://agentseller.temu.com/api/flash/compliance/dashBoard/main_page"
        
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
                "seller_cookie": "",
                "compliance_cookie": "",
                "mallid": "",
                "last_update": ""
            }
            self._save_config(default_config)
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
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
    
    def get_seller_cookie_from_browser(self) -> Tuple[str, str]:
        """从浏览器获取商家中心Cookie"""
        return self.get_website_cookies(self.seller_url)
    
    def get_compliance_cookie_from_browser(self) -> Tuple[str, str]:
        """从浏览器获取合规中心Cookie"""
        return self.get_website_cookies(self.compliance_url)
    
    def test_seller_api(self, cookie: str = None) -> Tuple[bool, str, Dict]:
        """
        测试商家中心API
        
        参数:
            cookie: 要测试的cookie，如果为None则使用配置中的cookie
            
        返回:
            tuple: (success, message, result_data)
        """
        if cookie is None:
            cookie = self.get_seller_cookie()
        
        if not cookie:
            return False, "Cookie为空，请先获取或配置Cookie", {}
        
        try:
            # 获取NetworkRequest实例
            request = self._get_request()
            
            # 临时更新配置中的商家中心cookie以便使用NetworkRequest
            original_cookie = self.config.get("seller_cookie", "")
            self.config["seller_cookie"] = cookie
            
            # 使用NetworkRequest发送GET请求
            result = request.post(self.seller_test_api, data={}, use_compliance=False)
            
            # 恢复原始cookie
            self.config["seller_cookie"] = original_cookie
            
            if not result:
                return False, "API请求失败，请检查Cookie是否有效", {}
            
            if result.get('success'):
                user_info = result.get('result', {})
                mall_info = ""
                if user_info.get('companyList'):
                    for company in user_info['companyList']:
                        if company.get('malInfoList'):
                            for mall in company['malInfoList']:
                                mall_info += f"店铺: {mall.get('mallName', 'N/A')} (ID: {mall.get('mallId', 'N/A')})\n"
                
                message = f"✅ 商家中心API测试成功！\n"
                message += f"用户ID: {user_info.get('userId', 'N/A')}\n"
                message += f"手机号: {user_info.get('maskMobile', 'N/A')}\n"
                message += f"角色: {', '.join(user_info.get('roleNameList', []))}\n"
                message += f"{mall_info}"
                
                return True, message, result
            else:
                return False, f"API返回失败: {result.get('errorMsg', '未知错误')}", result
                
        except Exception as e:
            return False, f"测试失败: {str(e)}", {}
    
    def test_compliance_api(self, cookie: str = None) -> Tuple[bool, str, Dict]:
        """
        测试合规中心API
        
        参数:
            cookie: 要测试的cookie，如果为None则使用配置中的cookie
            
        返回:
            tuple: (success, message, result_data)
        """
        if cookie is None:
            cookie = self.get_compliance_cookie()
        
        if not cookie:
            return False, "Cookie为空，请先获取或配置Cookie", {}
        
        try:
            # 获取NetworkRequest实例
            request = self._get_request()
            
            # 临时更新配置中的合规中心cookie以便使用NetworkRequest
            original_cookie = self.config.get("compliance_cookie", "")
            self.config["compliance_cookie"] = cookie
            
            # 使用NetworkRequest发送GET请求
            result = request.post(self.compliance_test_api,data={}, use_compliance=True)
            
            # 恢复原始cookie
            self.config["compliance_cookie"] = original_cookie
            
            if not result:
                return False, "API请求失败，请检查Cookie是否有效", {}
            
            if result.get('success'):
                compliance_data = result.get('result', {})
                
                # 统计合规信息
                addition_count = len(compliance_data.get('addition_compliance_board_list', []))
                accused_count = len(compliance_data.get('accused_violate_policy_board_list', []))
                
                # 计算总问题数
                total_issues = 0
                for item in compliance_data.get('addition_compliance_board_list', []):
                    total_issues += item.get('main_show_num', 0)
                for item in compliance_data.get('accused_violate_policy_board_list', []):
                    total_issues += item.get('main_show_num', 0)
                
                message = f"✅ 合规中心API测试成功！\n"
                message += f"合规补充项目: {addition_count} 个\n"
                message += f"违规指控项目: {accused_count} 个\n"
                message += f"待处理问题总数: {total_issues} 个\n"
                
                return True, message, result
            else:
                return False, f"API返回失败: {result.get('error_msg', '未知错误')}", result
                
        except Exception as e:
            return False, f"测试失败: {str(e)}", {}
            
    def get_seller_cookie(self) -> str:
        """获取商家中心cookie"""
        return self.config.get("seller_cookie", "")
        
    def get_compliance_cookie(self) -> str:
        """获取合规cookie"""
        return self.config.get("compliance_cookie", "")
        
    def get_mallid(self) -> str:
        """获取mallid"""
        return self.config.get("mallid", "")
        
    def update_config(self, seller_cookie: str = "", compliance_cookie: str = "", mallid: str = "") -> None:
        """更新配置"""
        if seller_cookie:
            self.config["seller_cookie"] = seller_cookie
        if compliance_cookie:
            self.config["compliance_cookie"] = compliance_cookie
        if mallid:
            self.config["mallid"] = mallid
            
        self.config["last_update"] = self._get_current_time()
        self._save_config(self.config)
        
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 