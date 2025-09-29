"""
竞价管理配置管理器
"""
import json
import os
import sys
from typing import Dict, List, Optional
from decimal import Decimal


class CategoryConfigManager:
    """商品类别配置管理器"""
    
    def __init__(self):
        # 处理打包环境和开发环境的路径差异
        if getattr(sys, 'frozen', False):
            # 打包环境：从可执行文件目录查找配置
            base_path = sys._MEIPASS
            self.config_file = os.path.join(base_path, 'config', 'category_config.json')
        else:
            # 开发环境：从源码目录查找配置
            self.config_file = os.path.join(os.path.dirname(__file__),'category_config.json')
        self._categories_cache = None
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"categories": []}
        except Exception as e:
            print(f"加载品类配置失败: {e}")
            return {"categories": []}
    
    def get_categories(self) -> List[Dict]:
        """获取所有品类配置"""
        if self._categories_cache is None:
            config = self._load_config()
            self._categories_cache = config.get("categories", [])
        return self._categories_cache
    
    def get_price_threshold_by_category_id(self, cate_id: int) -> Optional[float]:
        """根据品类ID获取价格阈值"""
        categories = self.get_categories()
        for category in categories:
            if category.get("cate_id") == cate_id:
                return float(category.get("price_threshold", 0))
        return None
    
    def get_price_threshold_by_category_ids(self, cate_id_list: List[int]) -> Optional[float]:
        """根据品类ID列表获取价格阈值（返回第一个匹配的）"""
        if not cate_id_list:
            return None
            
        for cate_id in cate_id_list:
            threshold = self.get_price_threshold_by_category_id(cate_id)
            if threshold is not None:
                return threshold
        return None
    
    def get_category_info_by_id(self, cate_id: int) -> Optional[Dict]:
        """根据品类ID获取完整的品类信息"""
        categories = self.get_categories()
        for category in categories:
            if category.get("cate_id") == cate_id:
                return category
        return None
    
    def get_code_mapping_by_category_id(self, cate_id: int) -> Optional[str]:
        """根据品类ID获取商品码映射"""
        category_info = self.get_category_info_by_id(cate_id)
        if category_info:
            return category_info.get("code_mapping")
        return None
    
    def get_code_mapping_by_category_ids(self, cate_id_list: List[int]) -> Optional[str]:
        """根据品类ID列表获取商品码映射（返回第一个匹配的）"""
        if not cate_id_list:
            return None
            
        for cate_id in cate_id_list:
            code_mapping = self.get_code_mapping_by_category_id(cate_id)
            if code_mapping is not None:
                return code_mapping
        return None
    
    def refresh_cache(self):
        """刷新缓存"""
        self._categories_cache = None


class BidConfigManager:
    """竞价配置管理器"""
    
    def __init__(self):
        # 处理打包环境和开发环境的路径差异
        if getattr(sys, 'frozen', False):
            # 打包环境：从可执行文件目录查找配置
            base_path = sys._MEIPASS
            self.config_file = os.path.join(base_path, 'config', 'bid_management_config.json')
        else:
            # 开发环境：从源码目录查找配置
            self.config_file = os.path.join(os.path.dirname(__file__), 'bid_management_config.json')
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"加载竞价配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "bid_reduction": 0.2,
            "max_page_size": 100,
            "random_delay_min": 1.0,
            "random_delay_max": 3.0,
            "adjust_reason": 6,
            "enable_price_threshold_check": True,  # 是否启用价格底线检查
            "last_update": "2025-01-28 15:00:00"
        }
    
    def save_config(self, config: Dict):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存竞价配置失败: {e}")
    
    def get_bid_reduction(self) -> float:
        """获取减价金额"""
        config = self._load_config()
        return float(config.get("bid_reduction", 0.2))
    
    def set_bid_reduction(self, reduction: float):
        """设置减价金额"""
        config = self._load_config()
        config["bid_reduction"] = reduction
        self.save_config(config)
    
    def get_max_page_size(self) -> int:
        """获取最大页面大小"""
        config = self._load_config()
        return int(config.get("max_page_size", 100))
    
    def is_price_threshold_check_enabled(self) -> bool:
        """是否启用价格底线检查"""
        config = self._load_config()
        return bool(config.get("enable_price_threshold_check", True))
    
    def get_random_delay_range(self) -> tuple:
        """获取随机延时范围"""
        config = self._load_config()
        return (
            float(config.get("random_delay_min", 1.0)),
            float(config.get("random_delay_max", 3.0))
        )
    
    def get_adjust_reason(self) -> int:
        """获取价格调整原因代码"""
        config = self._load_config()
        return int(config.get("adjust_reason", 6))


# 全局实例
category_config = CategoryConfigManager()
bid_config = BidConfigManager()
