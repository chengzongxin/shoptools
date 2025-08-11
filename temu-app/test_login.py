#!/usr/bin/env python3
"""
测试登录功能脚本
"""

import requests
import json

def test_login():
    """测试登录功能"""
    try:
        # 测试登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("🔐 测试登录功能...")
        print(f"用户名: {login_data['username']}")
        print(f"密码: {login_data['password']}")
        
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功！")
            print(f"Token: {data.get('access_token', '')[:50]}...")
            print(f"用户名: {data.get('username')}")
            
            # 测试获取用户信息
            token = data.get('access_token')
            if token:
                print("\n🔍 测试获取用户信息...")
                user_response = requests.get(
                    "http://localhost:8000/api/auth/me",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"用户信息状态码: {user_response.status_code}")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print("✅ 获取用户信息成功！")
                    print(f"用户ID: {user_data.get('id')}")
                    print(f"用户名: {user_data.get('username')}")
                    print(f"邮箱: {user_data.get('email')}")
                    print(f"是否管理员: {user_data.get('is_admin')}")
                else:
                    print("❌ 获取用户信息失败")
                    print(f"响应: {user_response.text}")
            
        else:
            print("❌ 登录失败")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    test_login() 