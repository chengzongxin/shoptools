#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temu API 测试脚本使用示例
展示如何使用 TemuAPITester 类进行各种测试
"""

from temu_api_test import TemuAPITester
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_basic_test():
    """基础测试示例"""
    print("=" * 60)
    print("🔧 基础测试示例")
    print("=" * 60)
    
    # 创建测试器实例
    tester = TemuAPITester()
    
    # 测试连接
    if tester.test_api_connection():
        print("✅ 连接测试成功")
        
        # 查询第一页数据
        data = tester.query_products(page=1, page_size=5)
        if data:
            print("✅ 数据查询成功")
            print(f"📊 响应状态: {data.get('success', '未知')}")
        else:
            print("❌ 数据查询失败")
    else:
        print("❌ 连接测试失败")

def example_multi_page_test():
    """多页测试示例"""
    print("\n" + "=" * 60)
    print("📄 多页测试示例")
    print("=" * 60)
    
    # 创建测试器实例
    tester = TemuAPITester()
    
    # 运行完整测试（3页数据）
    tester.run_test(pages=3)

def example_custom_test():
    """自定义测试示例"""
    print("\n" + "=" * 60)
    print("⚙️ 自定义测试示例")
    print("=" * 60)
    
    # 创建测试器实例
    tester = TemuAPITester()
    
    # 自定义查询参数
    pages_to_test = [1, 3, 5]  # 测试第1、3、5页
    page_size = 10  # 每页10条数据
    
    for page in pages_to_test:
        print(f"\n🔄 测试第 {page} 页，每页 {page_size} 条数据...")
        
        data = tester.query_products(page=page, page_size=page_size)
        if data:
            # 分析响应
            tester.analyze_response(data, page)
        else:
            print(f"❌ 第 {page} 页查询失败")

def example_data_analysis():
    """数据分析示例"""
    print("\n" + "=" * 60)
    print("📊 数据分析示例")
    print("=" * 60)
    
    # 创建测试器实例
    tester = TemuAPITester()
    
    # 获取数据
    data = tester.query_products(page=1, page_size=20)
    if data and data.get('success'):
        result = data.get('result', {})
        
        # 分析数据
        total = result.get('total', 0)
        products = result.get('pageItems', [])
        
        print(f"📊 总记录数: {total}")
        print(f"📦 当前页产品数: {len(products)}")
        
        # 分析产品类别
        categories = {}
        for product in products:
            cat_name = product.get('leafCat', {}).get('catName', '未知类别')
            categories[cat_name] = categories.get(cat_name, 0) + 1
        
        print("\n📋 产品类别分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count} 个产品")

def main():
    """主函数"""
    print("🛍️ Temu API 测试脚本使用示例")
    print("本示例展示了如何使用 TemuAPITester 进行各种测试")
    
    # 运行各种示例
    example_basic_test()
    example_multi_page_test()
    example_custom_test()
    example_data_analysis()
    
    print("\n🎉 所有示例运行完成！")
    print("📝 查看 data/ 目录中的输出文件")

if __name__ == "__main__":
    main() 