#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试确认上新UI界面
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.modules.confirm_upload.gui import ConfirmUploadTab

def test_ui():
    """测试UI界面"""
    root = tk.Tk()
    root.title("确认上新UI测试")
    root.geometry("800x600")
    
    # 创建确认上新标签页
    confirm_tab = ConfirmUploadTab(root)
    confirm_tab.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 添加测试按钮
    def test_days_value():
        days = confirm_tab.days_var.get()
        print(f"当前设置的天数: {days}")
        tk.messagebox.showinfo("测试", f"当前设置的天数: {days}")
    
    test_button = ttk.Button(root, text="测试天数设置", command=test_days_value)
    test_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_ui() 