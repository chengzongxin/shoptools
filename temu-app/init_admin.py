#!/usr/bin/env python3
"""
初始化管理员用户脚本
用于在本地开发环境中创建管理员用户
"""

import requests
import json

def init_admin_user():
    """初始化管理员用户"""
    try:
        # 调用后端API创建管理员用户
        response = requests.post(
            "http://localhost:8000/api/auth/init-admin",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 管理员用户初始化成功！")
            print(f"用户名: {result.get('username', 'admin')}")
            print(f"密码: {result.get('password', 'admin123')}")
            print("\n请使用以上凭据登录系统")
        else:
            print("❌ 初始化失败，可能管理员用户已存在")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始初始化管理员用户...")
    init_admin_user() 