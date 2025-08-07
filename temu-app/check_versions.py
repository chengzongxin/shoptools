#!/usr/bin/env python3
"""
检查当前安装的包版本
"""

import pkg_resources
import sys

def check_versions():
    """检查关键包的版本"""
    packages = ['bcrypt', 'passlib', 'fastapi', 'sqlalchemy', 'pymysql']
    
    print("📦 当前安装的包版本：")
    print("=" * 50)
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"{package:<15} : {version}")
        except pkg_resources.DistributionNotFound:
            print(f"{package:<15} : 未安装")
    
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    
    # 测试bcrypt兼容性
    print("\n🧪 测试bcrypt兼容性...")
    try:
        import bcrypt
        print(f"bcrypt模块版本: {bcrypt.__version__}")
        
        # 检查是否有__about__属性
        if hasattr(bcrypt, '__about__'):
            print("✅ bcrypt有__about__属性")
        else:
            print("❌ bcrypt缺少__about__属性（可能导致passlib错误）")
            
    except ImportError as e:
        print(f"❌ bcrypt导入失败: {e}")
    except Exception as e:
        print(f"❌ bcrypt测试失败: {e}")

if __name__ == "__main__":
    check_versions() 