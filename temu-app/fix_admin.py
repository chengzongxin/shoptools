#!/usr/bin/env python3
"""
修复管理员用户脚本
用于重新创建管理员用户，解决密码验证问题
"""

import requests
import json
from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_admin_user():
    """创建管理员用户"""
    try:
        # 生成新的密码哈希
        password = "admin123"
        password_hash = generate_password_hash(password)
        
        print("🔐 生成新的密码哈希...")
        print(f"密码: {password}")
        print(f"哈希: {password_hash}")
        
        # 调用后端API创建管理员用户
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            headers={"Content-Type": "application/json"},
            json={
                "username": "admin",
                "email": "admin@temu-app.com",
                "password": password
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 管理员用户创建成功！")
            print(f"用户ID: {result.get('id')}")
            print(f"用户名: {result.get('username')}")
            print(f"邮箱: {result.get('email')}")
            print(f"是否管理员: {result.get('is_admin')}")
            print(f"\n请使用以下凭据登录：")
            print(f"用户名: admin")
            print(f"密码: {password}")
        else:
            print("❌ 创建失败")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def test_password_verification():
    """测试密码验证"""
    print("\n🧪 测试密码验证功能...")
    
    password = "admin123"
    hash_value = generate_password_hash(password)
    
    # 测试验证
    is_valid = pwd_context.verify(password, hash_value)
    print(f"密码验证结果: {is_valid}")
    
    # 测试错误密码
    wrong_password = "wrong123"
    is_wrong = pwd_context.verify(wrong_password, hash_value)
    print(f"错误密码验证结果: {is_wrong}")
    
    return is_valid and not is_wrong

if __name__ == "__main__":
    print("🚀 开始修复管理员用户...")
    
    # 首先测试密码验证功能
    if test_password_verification():
        print("✅ 密码验证功能正常")
        create_admin_user()
    else:
        print("❌ 密码验证功能异常，请检查bcrypt版本") 