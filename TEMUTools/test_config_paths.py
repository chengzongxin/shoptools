#!/usr/bin/env python3
"""
测试配置文件路径处理是否正确
"""
import sys
import os
sys.path.append('src')

def test_config_paths():
    """测试配置文件路径"""
    print("=== 测试配置文件路径处理 ===")
    
    # 测试类别配置
    try:
        from modules.bid_management.config import category_config
        print(f"✅ 类别配置文件路径: {category_config.config_file}")
        print(f"✅ 配置文件存在: {os.path.exists(category_config.config_file)}")
        
        categories = category_config.get_categories()
        print(f"✅ 成功加载 {len(categories)} 个类别配置")
        
        # 测试具体功能
        threshold = category_config.get_price_threshold_by_category_id(29157)
        print(f"✅ 帆布袋价格阈值: {threshold}元")
        
    except Exception as e:
        print(f"❌ 类别配置加载失败: {e}")
    
    # 测试竞价配置
    try:
        from modules.bid_management.config import bid_config
        print(f"✅ 竞价配置文件路径: {bid_config.config_file}")
        print(f"✅ 配置文件存在: {os.path.exists(bid_config.config_file)}")
        
        bid_reduction = bid_config.get_bid_reduction()
        print(f"✅ 减价金额: {bid_reduction}元")
        
    except Exception as e:
        print(f"❌ 竞价配置加载失败: {e}")
    
    # 测试系统配置
    try:
        from modules.system_config.config import SystemConfig
        system_config = SystemConfig()
        print(f"✅ 系统配置文件路径: {system_config.config_file}")
        print(f"✅ 配置文件存在: {os.path.exists(system_config.config_file)}")
        
    except Exception as e:
        print(f"❌ 系统配置加载失败: {e}")
    
    # 测试核价配置功能
    try:
        from modules.price_review.crawler import PriceReviewCrawler
        print("✅ 核价模块导入成功")
        
        # 模拟商品数据测试
        mock_product = {
            'productId': 12345,
            'catIdList': [29157, 27011],  # 包含帆布袋类别
            'skcList': [
                {
                    'skuList': [{'extCode': 'CB_TEST_001'}]
                }
            ]
        }
        
        # 测试价格阈值获取逻辑
        from modules.bid_management.config import category_config
        cat_id_list = mock_product.get('catIdList', [])
        threshold = category_config.get_price_threshold_by_category_ids(cat_id_list)
        print(f"✅ 通过类别ID获取价格阈值: {threshold}元")
        
    except Exception as e:
        print(f"❌ 核价功能测试失败: {e}")
    
    print("\n=== 配置文件内容检查 ===")
    
    # 检查重要配置文件是否存在
    config_files = [
        'src/config/category_config.json',
        'src/config/bid_management_config.json',
        'src/config/system_config.json',
        'src/config/product_config.json',
        'src/config/violation_config.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            size = os.path.getsize(config_file)
            print(f"✅ {config_file} (大小: {size} 字节)")
        else:
            print(f"❌ {config_file} 不存在")

if __name__ == "__main__":
    test_config_paths()
