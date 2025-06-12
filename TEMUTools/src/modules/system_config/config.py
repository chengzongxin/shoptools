import json
import os
from typing import Dict, Optional

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