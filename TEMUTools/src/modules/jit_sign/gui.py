import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from typing import Optional
from .crawler import JitSignCrawler, JitSignProduct
from ..system_config.config import SystemConfig

class JitSignTab(ttk.Frame):
    """JIT签署标签页"""
    
    def __init__(self, parent):
        """初始化标签页
        
        Args:
            parent: 父容器
        """
        super().__init__(parent)
        self.config = SystemConfig()
        self.crawler: Optional[JitSignCrawler] = None
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self, text="参数设置")
        input_frame.pack(fill="x", padx=5, pady=5)
        self.create_input_fields(input_frame)
        
        # 创建进度条
        progress_frame = ttk.LabelFrame(self, text="处理进度")
        progress_frame.pack(fill="x", padx=5, pady=5)
        self.create_progress_bar(progress_frame)
        
        # 创建日志区域
        log_frame = ttk.LabelFrame(self, text="运行日志")
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.create_log_area(log_frame)
        
        # 创建按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)
        self.create_buttons(button_frame)
        
    def create_input_fields(self, parent):
        """创建输入字段
        
        Args:
            parent: 父容器
        """
        # 起始页
        ttk.Label(parent, text="起始页:").grid(row=0, column=0, padx=5, pady=5)
        self.start_page = ttk.Entry(parent, width=10)
        self.start_page.insert(0, "1")
        self.start_page.grid(row=0, column=1, padx=5, pady=5)
        
        # 结束页
        ttk.Label(parent, text="结束页:").grid(row=0, column=2, padx=5, pady=5)
        self.end_page = ttk.Entry(parent, width=10)
        self.end_page.insert(0, "1")
        self.end_page.grid(row=0, column=3, padx=5, pady=5)
        
        # 每页数量
        ttk.Label(parent, text="每页数量:").grid(row=0, column=4, padx=5, pady=5)
        self.page_size = ttk.Entry(parent, width=10)
        self.page_size.insert(0, "50")
        self.page_size.grid(row=0, column=5, padx=5, pady=5)
        
    def create_progress_bar(self, parent):
        """创建进度条
        
        Args:
            parent: 父容器
        """
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        
    def create_log_area(self, parent):
        """创建日志区域
        
        Args:
            parent: 父容器
        """
        self.log_text = tk.Text(parent, height=10)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def create_buttons(self, parent):
        """创建按钮
        
        Args:
            parent: 父容器
        """
        # 开始按钮
        self.start_button = ttk.Button(
            parent,
            text="开始签署",
            command=self.start_signing
        )
        self.start_button.pack(side="left", padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            parent,
            text="停止",
            command=self.stop_signing,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
    def setup_logging(self):
        """设置日志记录"""
        self.logger = logging.getLogger("JitSign")
        self.logger.setLevel(logging.INFO)
        
        # 添加文本处理器
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                
                def append():
                    self.text_widget.configure(state="normal")
                    self.text_widget.insert("end", msg + "\n")
                    self.text_widget.configure(state="disabled")
                    self.text_widget.see("end")
                    
                self.text_widget.after(0, append)
                
        handler = TextHandler(self.log_text)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def start_signing(self):
        """开始签署流程"""
        try:
            # 获取输入参数
            start_page = int(self.start_page.get())
            end_page = int(self.end_page.get())
            page_size = int(self.page_size.get())
            
            # 参数验证
            if start_page < 1 or end_page < start_page:
                messagebox.showerror("错误", "页码参数无效")
                return
                
            if page_size < 1 or page_size > 200:
                messagebox.showerror("错误", "每页数量必须在1-200之间")
                return
                
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            if not cookie:
                messagebox.showerror("错误", "请先配置卖家Cookie")
                return
                
            # 更新按钮状态
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # 创建爬虫实例
            self.crawler = JitSignCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress
            )
            
            # 启动处理线程
            thread = threading.Thread(
                target=self.run_signing,
                args=(start_page, end_page, page_size)
            )
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            
    def run_signing(self, start_page: int, end_page: int, page_size: int):
        """运行签署流程
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量
        """
        try:
            self.logger.info("开始批量签署JIT协议...")
            results = self.crawler.batch_process(
                start_page=start_page,
                end_page=end_page,
                page_size=page_size
            )
            
            # 统计结果
            total_success = sum(r["successNum"] for r in results)
            total_failed = sum(r["failedNum"] for r in results)
            
            self.logger.info(
                f"批量签署完成! 成功: {total_success}, 失败: {total_failed}"
            )
            
        except Exception as e:
            self.logger.error(f"处理过程发生错误: {str(e)}")
            
        finally:
            # 恢复按钮状态
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
    def stop_signing(self):
        """停止签署流程"""
        if self.crawler:
            self.crawler.stop()
            self.logger.info("正在停止处理...")
            
    def update_progress(self, value: int):
        """更新进度条
        
        Args:
            value: 进度值
        """
        self.progress_var.set(value) 