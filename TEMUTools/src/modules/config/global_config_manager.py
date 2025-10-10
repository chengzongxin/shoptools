import json
import os
import sys
from typing import Dict, List, Optional

class GlobalConfigManager:
    """全局配置管理器"""
    def __init__(self):
        # 处理打包环境和开发环境的路径差异
        if getattr(sys, 'frozen', False):
            # 打包环境：从可执行文件目录查找配置
            base_path = sys._MEIPASS
            self.config_file = os.path.join(base_path, 'config', 'global_config.json')
        else:
            # 开发环境：从源码目录查找配置
            self.config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'global_config.json'
            )
        self._config_cache = None


    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"加载全局配置失败: {e}")
            return {}

    def get_config(self) -> Dict:
        """获取全局配置"""
        if self._config_cache is None:
            self._config_cache = self._load_config()
        return self._config_cache

    def refresh_cache(self):
        """刷新缓存"""
        self._config_cache = None

    def update_config(self, updated_data: Dict) -> bool:
        """更新全局配置"""
        config = self.get_config()
        config.update(updated_data)
        return self.save_config(config)

    def save_config(self, config: Dict) -> bool:
        """保存全局配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.refresh_cache()
            return True
        except Exception as e:
            print(f"保存全局配置失败: {e}")
            return False


    def update_max_review_rounds(self, max_review_rounds: int):
        """更新最大审核轮数"""
        self.update_config({"max_review_rounds": max_review_rounds})
