"""核价模块配置文件"""

# 价格底线配置（单位：元）
PRICE_THRESHOLDS = {
    "CUSHION": 9,
    "drawing": 12.7,
    "CB": 10.7,
    "SLEEVE": 11.4,
    "SH": 8.7,
    "Scarf": 7.4,
    "Sock": 10.7,
    "Apron": 10.0,
    "bag": 33.0,
    "beanies": 11.4,
    "workcap": 13.5,
    "Handkerchief": 10.0,
    "WindproofMask": 13.5
}

def get_price_threshold(ext_code: str) -> float:
    """根据商品货号获取对应的价格底线
    
    Args:
        ext_code: 商品货号，例如 "drawing_#NLG8LEM"
        
    Returns:
        float: 价格底线（元），如果没有匹配的规则则返回None
    """
    # 将货号转换为小写以进行不区分大小写的匹配
    ext_code = ext_code.lower()
    
    # 遍历所有价格底线规则
    for prefix, threshold in PRICE_THRESHOLDS.items():
        if ext_code.startswith(prefix.lower()):
            return threshold
            
    return None 