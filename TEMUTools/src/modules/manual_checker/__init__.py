"""
说明书排查模块

主要功能:
1. 查询所有未上传说明书的商品（库存>=1）
2. 批量将这些商品的库存设为0（下架处理）
3. 库存<990的商品跳过并记录，需要手动处理
"""

from .crawler import ManualChecker, ManualProduct
from .gui import ManualCheckerGUI

__all__ = [
    'ManualChecker',
    'ManualProduct',
    'ManualCheckerGUI'
]

