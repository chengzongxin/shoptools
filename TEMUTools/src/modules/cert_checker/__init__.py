"""
资质排查模块

主要功能:
1. 查询所有资质类型（排除GCC）
2. 查询所有触发资质要求的商品
3. 批量将这些商品的库存设为0（下架处理）
"""

from .crawler import CertChecker, CertType, CertProduct
from .gui import CertCheckerGUI

__all__ = [
    'CertChecker',
    'CertType',
    'CertProduct',
    'CertCheckerGUI'
]
