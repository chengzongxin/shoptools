import logging
import tkinter as tk
from tkinter import ttk
from .logger import Logger

class LogHandler(logging.Handler):
    """自定义日志处理器,用于将日志输出到GUI"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        def append():
            try:
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.configure(state='disabled')
            except tk.TclError:
                # GUI组件已销毁，忽略错误
                pass
        
        # 在主线程中更新GUI，添加异常处理
        try:
            self.text_widget.after(0, append)
        except RuntimeError:
            # 主线程还未进入主循环或已退出，直接输出到控制台
            print(f"[GUI未就绪] {msg}")
        except tk.TclError:
            # GUI组件已销毁，忽略错误
            pass

class LogFrame(ttk.LabelFrame):
    """日志显示框架"""
    
    def __init__(self, parent):
        super().__init__(parent, text="系统日志", padding="5")
        self._init_ui()
        self._setup_logger()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建文本框和滚动条
        self.text_area = tk.Text(self, height=10, width=80, state='disabled')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        # 布局
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def _setup_logger(self):
        """设置日志处理器"""
        # 创建自定义处理器
        handler = LogHandler(self.text_area)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        # 添加到根日志记录器
        logger = Logger()
        logger.logger.addHandler(handler)
        
    def clear(self):
        """清空日志显示"""
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled') 