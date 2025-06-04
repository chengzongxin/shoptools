class PriceMapper:
    """
    价格映射类
    负责处理货号和价格的对应关系
    """
    def __init__(self, debug=True):
        """
        初始化价格映射器
        :param debug: 是否开启调试模式
        """
        self.debug = debug
        # 直接映射货号前缀到价格
        self.price_mapping = {
            "drawing": 12.7,
            "CB": 10.7,
            "SLEEVE": 11.4,
            "SH": 8.7,
            "Scarf": 7.4,
            "Sock": 10.7,
            "Apron": 10.0
        }

    def clean_sku(self, sku):
        """
        清理货号，移除多余文字
        :param sku: 原始货号文本
        :return: 清理后的货号
        """
        try:
            # 移除"货号："前缀
            if "货号：" in sku:
                sku = sku.replace("货号：", "")
            
            # 移除"SPU："前缀
            if "SPU：" in sku:
                sku = sku.replace("SPU：", "")
            
            # 移除多余空格
            sku = sku.strip()
            
            if self.debug:
                print(f"清理后的货号: {sku}")
            
            return sku
            
        except Exception as e:
            print(f"清理货号失败: {str(e)}")
            return sku

    def get_min_price(self, sku):
        """
        从货号中获取价格
        :param sku: 货号
        :return: 价格或None
        """
        try:
            # 清理货号
            sku = self.clean_sku(sku)
            
            # 提取货号前缀（第一个下划线之前的部分）
            prefix = sku.split('_')[0] if '_' in sku else sku
            
            # 获取价格
            price = self.price_mapping.get(prefix)
            
            if price is None:
                if self.debug:
                    print(f"未找到货号 {sku} 对应的价格")
                return None
            
            if self.debug:
                print(f"原始货号: {sku}")
                print(f"提取的前缀: {prefix}")
                print(f"对应价格: {price}")
            
            return price
            
        except Exception as e:
            print(f"获取价格失败: {str(e)}")
            return None

    def get_price_info(self, sku):
        """
        获取货号对应的价格信息
        :param sku: 货号
        :return: (货号前缀, 价格) 元组
        """
        try:
            # 清理货号
            sku = self.clean_sku(sku)
            
            # 提取货号前缀
            prefix = sku.split('_')[0] if '_' in sku else sku
            
            # 获取价格
            price = self.get_min_price(sku)
            
            return prefix, price
            
        except Exception as e:
            print(f"获取价格信息失败: {str(e)}")
            return None, None 