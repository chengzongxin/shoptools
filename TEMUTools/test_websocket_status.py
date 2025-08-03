#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试WebSocket状态显示功能
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_websocket_status():
    """测试WebSocket状态显示"""
    root = tk.Tk()
    root.title("WebSocket状态测试")
    root.geometry("800x600")
    
    # 创建系统配置标签页
    from modules.system_config.gui import SystemConfigTab
    
    # 创建notebook容器
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 添加系统配置标签页
    config_tab = SystemConfigTab(notebook)
    notebook.add(config_tab, text="系统配置")
    
    # 添加说明标签页
    info_frame = ttk.Frame(notebook)
    notebook.add(info_frame, text="使用说明")
    
    info_text = tk.Text(info_frame, wrap=tk.WORD, padx=10, pady=10)
    info_text.pack(fill=tk.BOTH, expand=True)
    
    info_content = """
WebSocket状态显示功能说明：

1. 状态指示器：
   - ❌ 红色：服务器未运行或模块未安装
   - ⏳ 橙色：服务器运行中，等待连接
   - ✅ 绿色：已连接，显示连接数

2. 操作步骤：
   - 点击"启动WebSocket服务器"按钮启动服务器
   - 确保Chrome插件已连接（插件会自动连接到localhost:8765）
   - 状态会自动更新，每2秒检查一次
   - 可以点击"停止WebSocket服务器"按钮停止服务器

3. 功能特点：
   - 实时显示连接状态
   - 显示连接的客户端数量
   - 自动检测服务器运行状态
   - 支持手动启动/停止服务器

4. 注意事项：
   - 需要安装websockets依赖：pip install websockets
   - Chrome插件需要配置正确的WebSocket地址
   - 服务器默认监听localhost:8765端口
    """
    
    info_text.insert('1.0', info_content)
    info_text.config(state='disabled')
    
    def on_closing():
        """窗口关闭时的处理"""
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("WebSocket状态测试界面已启动")
    print("请观察状态指示器的变化")
    
    root.mainloop()

if __name__ == "__main__":
    test_websocket_status() 