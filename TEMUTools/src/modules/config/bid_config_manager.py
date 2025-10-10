import json
import os
import sys
from typing import Dict, List, Optional

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
            self.config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'bid_management_config.json'
            )

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
