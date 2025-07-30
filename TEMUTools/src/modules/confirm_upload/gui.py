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
        # self.create_product_list(main_frame)
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_input_fields(self, parent):
        """创建输入字段"""
        # 创建一个子框架来容纳输入字段
        input_frame = ttk.LabelFrame(parent, text="过滤设置", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 过滤天数设置
        ttk.Label(input_frame, text="过滤天数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.days_var = tk.StringVar(value="5")
        self.days_entry = ttk.Entry(input_frame, textvariable=self.days_var, width=10)
        self.days_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(input_frame, text="天（只处理最近N天内的商品）").grid(row=0, column=2, sticky=tk.W)
        
        # 配置输入框架的网格权重
        input_frame.columnconfigure(2, weight=1)
        
    def create_progress_bar(self, parent):
        """创建进度条"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 添加进度标签
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, sticky=tk.W)
        
        # 配置进度框架的网格权重
        progress_frame.columnconfigure(0, weight=1)
        
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        log_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 批量处理按钮
        self.batch_button = ttk.Button(
            button_frame,
            text="开始批量确认上新",
            command=self.start_batch_processing
        )
        self.batch_button.grid(row=0, column=0, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_processing,
            state='disabled'
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
    # def create_product_list(self, parent):
    #     """创建商品列表"""
    #     # 创建表格
    #     columns = ("商品ID", "商品名称", "货号", "价格", "买家", "创建时间")
    #     self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
    #     # 设置列标题
    #     for col in columns:
    #         self.tree.heading(col, text=col)
    #         self.tree.column(col, width=100)
            
    #     # 添加滚动条
    #     scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
    #     self.tree.configure(yscrollcommand=scrollbar.set)
        
    #     # 放置表格和滚动条
    #     self.tree.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    #     scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        
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
        
    def start_batch_processing(self):
        """开始批量处理确认上新"""
        try:
            # 获取过滤天数
            try:
                days_filter = int(self.days_var.get())
                if days_filter <= 0 or days_filter > 365:
                    messagebox.showerror("错误", "过滤天数必须在1-365之间")
                    return
            except ValueError:
                messagebox.showerror("错误", "过滤天数必须是数字")
                return

            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置Cookie")
                return
                
            # 显示确认对话框
            if not messagebox.askyesno("确认", f"确定要批量处理最近 {days_filter} 天内的确认上新吗？"):
                return
                
            # 禁用按钮
            self.batch_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # 设置停止标志
            self._stop_flag = False
            
            # 清空进度条
            self.progress_var.set(0)
            
            # 创建爬虫实例
            self.crawler = ConfirmUploadCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress,
                stop_flag_callback=lambda: self._stop_flag
            )
            
            # 在新线程中运行批量处理
            self.crawler_thread = threading.Thread(
                target=self.run_batch_processing,
                args=(days_filter,)
            )
            self.crawler_thread.start()
            
        except Exception as e:
            self.logger.error(f"启动批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"启动批量处理失败: {str(e)}")
            
    def run_batch_processing(self, days_filter):
        """运行批量处理"""
        try:
            results = self.crawler.batch_process(days_filter)
            
            # 统计处理结果
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
            
            # 显示处理结果
            message = f"批量处理完成\n成功: {success_count} 个\n失败: {fail_count} 个\n过滤天数: {days_filter} 天"
            self.logger.info(message)
            messagebox.showinfo("完成", message)
            
        except Exception as e:
            self.logger.error(f"批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"批量处理失败: {str(e)}")
        finally:
            self.batch_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def stop_processing(self):
        """停止处理"""
        self._stop_flag = True
        self.logger.info("用户请求停止处理")
        messagebox.showinfo("提示", "正在停止处理，请稍候...")
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%") 