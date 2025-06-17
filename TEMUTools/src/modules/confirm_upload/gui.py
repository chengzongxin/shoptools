import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import logging
import os
from datetime import datetime
from .crawler import ConfirmUploadCrawler, UploadProduct
from ..system_config.config import SystemConfig

class ConfirmUploadTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 初始化默认值
        self.config = SystemConfig()
        self.current_data = []  # 存储当前获取的数据
        
        # 创建日志目录
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置UI
        self.setup_ui()
        
        # 配置日志处理器
        self.setup_logging()
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建输入字段
        self.create_input_fields(main_frame)
        
        # 创建进度条
        self.create_progress_bar(main_frame)
        
        # 创建日志显示区域
        self.create_log_area(main_frame)
        
        # 创建按钮
        self.create_buttons(main_frame)
        
        # 创建商品列表
        self.create_product_list(main_frame)
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def create_input_fields(self, parent):
        """创建输入字段"""
        # 起始页输入
        ttk.Label(parent, text="起始页:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_page_var = tk.StringVar(value="1")
        self.start_page_entry = ttk.Entry(parent, textvariable=self.start_page_var, width=10)
        self.start_page_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 结束页输入
        ttk.Label(parent, text="结束页:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.end_page_var = tk.StringVar(value="1")
        self.end_page_entry = ttk.Entry(parent, textvariable=self.end_page_var, width=10)
        self.end_page_entry.grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 每页数量输入
        ttk.Label(parent, text="每页数量:").grid(row=0, column=4, sticky=tk.W, pady=5)
        self.page_size_var = tk.StringVar(value="100")
        self.page_size_entry = ttk.Entry(parent, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=0, column=5, sticky=tk.W, pady=5)
        
        # 配置网格权重
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
        parent.columnconfigure(5, weight=1)
        
    def create_progress_bar(self, parent):
        """创建进度条"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, state='disabled')
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def create_buttons(self, parent):
        """创建按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 开始爬取按钮
        self.start_button = ttk.Button(
            button_frame,
            text="获取商品列表",
            command=self.start_crawling
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # 批量处理按钮
        self.batch_button = ttk.Button(
            button_frame,
            text="批量确认上新",
            command=self.start_batch_processing
        )
        self.batch_button.grid(row=0, column=1, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_crawling,
            state='disabled'
        )
        self.stop_button.grid(row=0, column=2, padx=5)
        
    def create_product_list(self, parent):
        """创建商品列表"""
        # 创建表格
        columns = ("商品ID", "商品名称", "货号", "价格", "买家", "创建时间")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.tree.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        
    def setup_logging(self):
        """设置日志处理器"""
        # 创建自定义日志处理器
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                    self.text_widget.configure(state='disabled')
                self.text_widget.after(0, append)
        
        # 创建独立的logger
        self.logger = logging.getLogger('confirm_upload')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        # 添加文件处理器
        log_file = os.path.join(self.log_dir, f'confirm_upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # 添加一个初始日志
        self.logger.info("批量确认上新工具已初始化")
        self.logger.info(f"日志文件保存在: {log_file}")
        
    def start_crawling(self):
        """开始爬取数据"""
        try:
            # 获取输入参数
            start_page = int(self.start_page_var.get())
            end_page = int(self.end_page_var.get())
            page_size = int(self.page_size_var.get())
            
            # 验证输入
            if start_page <= 0 or end_page <= 0 or page_size <= 0:
                messagebox.showerror("错误", "页码和每页数量必须大于0")
                return
                
            if start_page > end_page:
                messagebox.showerror("错误", "起始页不能大于结束页")
                return
                
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置Cookie")
                return
                
            # 禁用开始按钮,启用停止按钮
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # 清空进度条
            self.progress_var.set(0)
            
            # 创建爬虫实例
            self.crawler = ConfirmUploadCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress
            )
            
            # 在新线程中运行爬虫
            self.crawler_thread = threading.Thread(
                target=self.run_crawler,
                args=(start_page, end_page, page_size)
            )
            self.crawler_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            self.logger.error(f"启动爬虫失败: {str(e)}")
            messagebox.showerror("错误", f"启动爬虫失败: {str(e)}")
            
    def run_crawler(self, start_page: int, end_page: int, page_size: int):
        """运行爬虫"""
        try:
            self.current_data = self.crawler.crawl(start_page, end_page, page_size)
            
            # 更新商品列表
            self.update_product_list()
            
            self.logger.info(f"成功获取 {len(self.current_data)} 条数据")
            messagebox.showinfo("成功", f"成功获取 {len(self.current_data)} 条数据")
            
        except Exception as e:
            self.logger.error(f"爬取数据失败: {str(e)}")
            messagebox.showerror("错误", f"爬取数据失败: {str(e)}")
        finally:
            # 恢复按钮状态
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def stop_crawling(self):
        """停止爬取"""
        if hasattr(self, 'crawler'):
            self.crawler.stop()
            self.logger.info("已停止爬取")
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        
    def update_product_list(self):
        """更新商品列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.logger.info(f"开始更新商品列表，当前数据条数: {len(self.current_data)}")
            
        # 添加新数据
        for product in self.current_data:
            created_at = datetime.fromtimestamp(product.productCreatedAt/1000).strftime('%Y-%m-%d %H:%M:%S')
            
            self.logger.debug(f"添加商品到列表: ID={product.productId}, 名称={product.productName}")
            
            self.tree.insert('', 'end', values=(
                product.productId,
                product.productName,
                product.extCode,
                product.supplierPrice,
                product.buyerName,
                created_at
            ))
            
    def start_batch_processing(self):
        """开始批量处理确认上新"""
        try:
            start_page = int(self.start_page_var.get())
            end_page = int(self.end_page_var.get())
            page_size = int(self.page_size_var.get())
            
            if start_page <= 0 or end_page <= 0 or page_size <= 0:
                messagebox.showerror("错误", "页数和每页数量必须大于0")
                return
                
            if start_page > end_page:
                messagebox.showerror("错误", "起始页不能大于结束页")
                return

            if page_size > 50:
                messagebox.showerror("错误", "每页数量不能大于50")
                return
                
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置Cookie")
                return
                
            # 显示确认对话框
            if not messagebox.askyesno("确认", f"确定要批量处理 {start_page} 到 {end_page} 页的确认上新吗？"):
                return
                
            # 禁用按钮
            self.start_button.config(state='disabled')
            self.batch_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # 清空进度条
            self.progress_var.set(0)
            
            # 创建爬虫实例
            self.crawler = ConfirmUploadCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress
            )
            
            # 直接在当前线程中运行批量处理
            self.run_batch_processing(start_page, end_page, page_size)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            self.logger.error(f"启动批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"启动批量处理失败: {str(e)}")
            
    def run_batch_processing(self, start_page, end_page, page_size):
        """运行批量处理"""
        try:
            results = self.crawler.batch_process(start_page, end_page, page_size)
            
            # 统计处理结果
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
            
            # 更新商品列表
            self.update_product_list()
            
            # 显示处理结果
            message = f"批量处理完成\n成功: {success_count} 个\n失败: {fail_count} 个"
            self.logger.info(message)
            messagebox.showinfo("完成", message)
            
        except Exception as e:
            self.logger.error(f"批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"批量处理失败: {str(e)}")
        finally:
            # 恢复按钮状态
            self.start_button.config(state='normal')
            self.batch_button.config(state='normal')
            self.stop_button.config(state='disabled') 