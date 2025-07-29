import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.system_config.gui import SystemConfigTab

def main():
    """测试系统配置功能"""
    root = tk.Tk()
    root.title("系统配置测试")
    root.geometry("1000x700")
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill="both")
    
    # 创建系统配置标签页
    config_tab = SystemConfigTab(main_frame)
    config_tab.pack(expand=True, fill="both")
    
    root.mainloop()

if __name__ == "__main__":
    main() 