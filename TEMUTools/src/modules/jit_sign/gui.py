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

        self.progress_label = ttk.Label(parent, text="0/0")
        self.progress_label.pack(fill="x", padx=5, pady=2)
        
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
            text="开始批量签署",
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
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置好卖家Cookie")
                return
                
            # 更新按钮状态
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # 设置停止标志
            self._stop_flag = False
            
            # 创建爬虫实例
            self.crawler = JitSignCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress,
                stop_flag_callback=lambda: self._stop_flag
            )
            
            # 启动处理线程
            thread = threading.Thread(
                target=self.run_signing
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"启动过程发生错误: {str(e)}")
            messagebox.showerror("错误", f"启动失败: {str(e)}")
            
    def run_signing(self):
        """运行签署流程"""
        try:
            self.logger.info("开始批量签署JIT协议...")
            self.update_progress(0, 0)
            results = self.crawler.batch_process()
            
            # 统计结果
            if results:
                total_success = sum(r.get("successNum", 0) for r in results)
                total_failed = sum(r.get("failedNum", 0) for r in results)
                self.logger.info(
                    f"批量签署完成! 成功: {total_success}, 失败: {total_failed}"
                )
            else:
                self.logger.info("批量签署任务结束。")
            
        except Exception as e:
            self.logger.error(f"处理过程发生错误: {str(e)}")
            
        finally:
            # 恢复按钮状态
            self.after(0, lambda: self.start_button.configure(state="normal"))
            self.after(0, lambda: self.stop_button.configure(state="disabled"))
            
    def stop_signing(self):
        """停止签署流程"""
        self._stop_flag = True
        self.logger.info("用户请求停止签署")
        messagebox.showinfo("提示", "正在停止签署，请稍候...")
        
    def update_progress(self, current: int, total: int):
        """更新进度条
        
        Args:
            current: 当前进度
            total: 总数
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{current}/{total}")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="0/0")
        self.update_idletasks() 