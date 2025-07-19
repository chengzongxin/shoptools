#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的UI测试 - 验证输入框显示
"""

import tkinter as tk
from tkinter import ttk, messagebox

def create_test_ui():
    """创建测试UI"""
    root = tk.Tk()
    root.title("确认上新过滤设置测试")
    root.geometry("600x400")
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 创建输入字段框架
    input_frame = ttk.LabelFrame(main_frame, text="过滤设置", padding="5")
    input_frame.pack(fill=tk.X, pady=5)
    
    # 过滤天数设置
    ttk.Label(input_frame, text="过滤天数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
    days_var = tk.StringVar(value="5")
    days_entry = ttk.Entry(input_frame, textvariable=days_var, width=10)
    days_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
    ttk.Label(input_frame, text="天（只处理最近N天内的商品）").grid(row=0, column=2, sticky=tk.W)
    
    # 配置网格权重
    input_frame.columnconfigure(2, weight=1)
    
    # 创建进度条框架
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=5)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    progress_label = ttk.Label(progress_frame, text="0%")
    progress_label.pack(side=tk.RIGHT)
    
    # 测试按钮
    def test_value():
        days = days_var.get()
        messagebox.showinfo("测试", f"当前设置的天数: {days}")
    
    test_button = ttk.Button(main_frame, text="测试天数设置", command=test_value)
    test_button.pack(pady=10)
    
    # 说明文本
    info_text = tk.Text(main_frame, height=8, width=60, state='disabled')
    info_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # 添加说明信息
    info_text.configure(state='normal')
    info_text.insert('1.0', """确认上新时间过滤功能说明：

1. 过滤天数：设置要处理最近多少天内的商品
   - 默认值：5天
   - 范围：1-365天
   - 只处理指定天数内创建的商品

2. 时间计算：
   - 结束时间：当前时间
   - 开始时间：当前时间 - 过滤天数
   - 时间戳：毫秒级时间戳

3. API参数：
   - timeType: 1
   - timeBegin: 开始时间戳
   - timeEnd: 结束时间戳
   - supplierTodoTypeList: [6] (待确认上新)

4. 使用流程：
   - 设置过滤天数
   - 点击"开始批量确认上新"
   - 系统自动处理符合条件的商品

这个功能可以避免处理过期的商品，提高处理效率。""")
    info_text.configure(state='disabled')
    
    root.mainloop()

if __name__ == "__main__":
    create_test_ui() 