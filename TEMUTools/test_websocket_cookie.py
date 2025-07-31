#!/usr/bin/env python3
"""
WebSocket Cookie获取功能测试
用于测试WebSocket服务器和Cookie获取功能
"""

import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.system_config.websocket_cookie import get_websocket_manager, start_websocket_server

def test_websocket_server():
    """测试WebSocket服务器"""
    print("🧪 测试WebSocket Cookie获取功能")
    print("=" * 50)
    
    # 启动WebSocket服务器
    print("1. 启动WebSocket服务器...")
    try:
        start_websocket_server()
        print("✅ WebSocket服务器已启动 (ws://localhost:8765)")
    except Exception as e:
        print(f"❌ WebSocket服务器启动失败: {e}")
        return
    
    # 获取管理器实例
    manager = get_websocket_manager()
    
    print("\n2. 等待Chrome插件连接...")
    print("   请在Chrome浏览器中启动配套插件")
    print("   插件应连接到: ws://localhost:8765")
    
    # 等待连接
    timeout = 30
    for i in range(timeout):
        if manager.is_connected():
            print(f"\n✅ Chrome插件已连接! ({i+1}秒)")
            break
        else:
            print(f"   等待连接... ({i+1}/{timeout}秒)", end='\r')
            time.sleep(1)
    else:
        print(f"\n❌ 等待超时，未检测到Chrome插件连接")
        return
    
    print("\n3. 测试Cookie获取...")
    
    # 测试获取Cookie
    domain = "agentseller.temu.com"
    cookie_string, error_msg = manager.get_domain_cookies(domain)
    
    if error_msg:
        print(f"❌ 获取Cookie失败: {error_msg}")
    else:
        print(f"✅ Cookie获取成功!")
        print(f"   域名: {domain}")
        print(f"   Cookie长度: {len(cookie_string)} 字符")
        print(f"   Cookie预览: {cookie_string[:100]}...")
    
    print("\n🎉 测试完成!")

def main():
    """主函数"""
    try:
        test_websocket_server()
    except KeyboardInterrupt:
        print("\n👋 测试已终止")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    main()