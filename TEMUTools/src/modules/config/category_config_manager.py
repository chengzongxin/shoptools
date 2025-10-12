import json
import os
import sys
from typing import Dict, List, Optional

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
            self.config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'category_config.json'
            )
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

    def get_categories(self, enabled_only: bool = False) -> List[Dict]:
        """
        获取品类配置

        参数:
            enabled_only: 是否只返回启用的品类，默认False返回所有
        """
        if self._categories_cache is None:
            config = self._load_config()
            self._categories_cache = config.get("categories", [])

        if enabled_only:
            return [cat for cat in self._categories_cache if cat.get("enabled", True)]
        return self._categories_cache

    def get_price_threshold_by_category_id(self, cate_id: int, enable_only=False) -> Optional[float]:
        """根据品类ID获取价格阈值"""
        categories = self.get_categories(enabled_only=enable_only)
        for category in categories:
            if category.get("cate_id") == cate_id:
                return float(category.get("price_threshold", 0))
        return None

    def get_price_threshold_by_category_ids(self, cate_id_list: List[int]) -> Optional[float]:
        """根据品类ID列表获取价格阈值（返回第一个匹配的）"""
        if not cate_id_list:
            return None

        for cate_id in cate_id_list:
            threshold = self.get_price_threshold_by_category_id(cate_id, enable_only=True)
            if threshold is not None:
                return threshold
        return None

    def get_category_info_by_id(self, cate_id: int) -> Optional[Dict]:
        """根据品类ID获取完整的品类信息（保留向后兼容）"""
        categories = self.get_categories()
        for category in categories:
            if category.get("cate_id") == cate_id:
                return category
        return None

    def get_category_by_id(self, category_id: int) -> Optional[Dict]:
        """根据内部唯一ID获取品类信息"""
        categories = self.get_categories()
        for category in categories:
            if category.get("id") == category_id:
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

    def _get_next_id(self, categories: List[Dict]) -> int:
        """获取下一个自增ID"""
        if not categories:
            return 1
        max_id = max(cat.get('id', 0) for cat in categories)
        return max_id + 1

    def save_categories(self, categories: List[Dict]) -> bool:
        """保存品类配置"""
        try:
            from datetime import datetime

            # 确保每个品类都有ID，如果没有则自动分配
            for category in categories:
                if 'id' not in category or category['id'] is None:
                    category['id'] = self._get_next_id(categories)

            config = {
                "categories": categories,
                "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.refresh_cache()
            return True
        except Exception as e:
            print(f"保存品类配置失败: {e}")
            return False

    def add_category(self, category: Dict) -> bool:
        """添加品类"""
        categories = self.get_categories()
        categories.append(category)
        return self.save_categories(categories)

    def update_category(self, category_id: int, updated_data: Dict, use_internal_id: bool = True) -> bool:
        """
        更新品类信息

        参数:
            category_id: 品类ID（内部ID或cate_id）
            updated_data: 要更新的数据
            use_internal_id: True表示使用内部唯一ID，False表示使用cate_id（默认True）
        """
        categories = self.get_categories()
        for i, cat in enumerate(categories):
            if use_internal_id:
                if cat.get("id") == category_id:
                    categories[i].update(updated_data)
                    return self.save_categories(categories)
            else:
                if cat.get("cate_id") == category_id:
                    categories[i].update(updated_data)
                    return self.save_categories(categories)
        return False

    def delete_category(self, category_id: int, use_internal_id: bool = True) -> bool:
        """
        删除品类

        参数:
            category_id: 品类ID（内部ID或cate_id）
            use_internal_id: True表示使用内部唯一ID，False表示使用cate_id（默认True）
        """
        categories = self.get_categories()
        if use_internal_id:
            categories = [cat for cat in categories if cat.get("id") != category_id]
        else:
            categories = [cat for cat in categories if cat.get("cate_id") != category_id]
        return self.save_categories(categories)

    def get_images_dir(self) -> str:
        """获取图片目录路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_path, 'assets', 'images')