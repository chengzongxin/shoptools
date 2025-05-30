import tkinter as tk
from tkinter import ttk
import os
from modules.product_list.gui import ProductListTab

class TEMUToolsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEMU工具集")
        self.root.geometry("800x600")
        
        # 创建notebook（选项卡控件）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 创建各个功能模块的选项卡
        self.create_product_list_tab()
        self.create_template_tab()
        self.create_inventory_tab()
        
    def create_product_list_tab(self):
        """商品列表管理选项卡"""
        product_list_tab = ProductListTab(self.notebook)
        self.notebook.add(product_list_tab, text="商品列表管理")
        
    def create_template_tab(self):
        """商品码模板选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="商品码模板")
        
        # 添加说明标签
        label = ttk.Label(frame, text="商品码模板功能开发中...")
        label.pack(pady=20)
        
    def create_inventory_tab(self):
        """库存模板选项卡"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="库存模板")
        
        # 添加说明标签
        label = ttk.Label(frame, text="库存模板功能开发中...")
        label.pack(pady=20)

def main():
    root = tk.Tk()
    app = TEMUToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 