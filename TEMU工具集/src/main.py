import tkinter as tk
from tkinter import ttk
import logging
from modules.product_list.gui import ProductListGUI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TEMU工具集")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个功能模块的选项卡
        self.create_product_list_tab()
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def create_product_list_tab(self):
        """创建商品列表管理选项卡"""
        product_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(product_list_frame, text="商品列表管理")
        
        # 创建商品列表管理GUI
        self.product_list_gui = ProductListGUI(product_list_frame)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main() 