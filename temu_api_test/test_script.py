#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的测试脚本，用于验证主脚本的基本功能
"""

def test_imports():
    """测试是否能正确导入所需的模块"""
    try:
        import requests
        import json
        import time
        import logging
        from typing import Dict, Any, Optional
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_requests_connection():
    """测试网络连接"""
    try:
        import requests
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ 网络连接测试成功")
            return True
        else:
            print(f"⚠️ 网络连接测试返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 网络连接测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 开始运行基础测试...")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        print("❌ 模块导入测试失败，请检查依赖安装")
        return
    
    # 测试网络连接
    if not test_requests_connection():
        print("❌ 网络连接测试失败，请检查网络设置")
        return
    
    print("\n🎉 基础测试全部通过！")
    print("📝 现在可以运行主脚本: python3 temu_api_test.py")

if __name__ == "__main__":
    main() 