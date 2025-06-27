import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from typing import Optional
from .crawler import StockBatchSetter
from ..system_config.config import SystemConfig

class StockSetterTab(ttk.Frame):
    """批量设置库存标签页"""
    
    def __init__(self, parent):
        """初始化标签页
        
        Args:
            parent: 父容器
        """
        super().__init__(parent)
        self.config = SystemConfig()
        self.crawler: Optional[StockBatchSetter] = None
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建参数设置区域
        param_frame = ttk.LabelFrame(self, text="参数设置")
        param_frame.pack(fill="x", padx=5, pady=5)
        self.create_param_area(param_frame)
        
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
        
    def create_param_area(self, parent):
        """创建参数设置区域
        
        Args:
            parent: 父容器
        """
        # 库存数量设置
        stock_frame = ttk.Frame(parent)
        stock_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(stock_frame, text="设置库存数量:").pack(side="left")
        self.stock_var = tk.StringVar(value="1000")
        self.stock_entry = ttk.Entry(stock_frame, textvariable=self.stock_var, width=10)
        self.stock_entry.pack(side="left", padx=5)
        ttk.Label(stock_frame, text="(个)").pack(side="left")
        
        # 线程数设置
        thread_frame = ttk.Frame(parent)
        thread_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(thread_frame, text="并发线程数:").pack(side="left")
        self.thread_var = tk.StringVar(value="5")
        self.thread_entry = ttk.Entry(thread_frame, textvariable=self.thread_var, width=10)
        self.thread_entry.pack(side="left", padx=5)
        ttk.Label(thread_frame, text="(建议1-10)").pack(side="left")
        
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
            text="开始批量设置库存",
            command=self.start_setting
        )
        self.start_button.pack(side="left", padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            parent,
            text="停止",
            command=self.stop_setting,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        # 清空日志按钮
        self.clear_button = ttk.Button(
            parent,
            text="清空日志",
            command=self.clear_log
        )
        self.clear_button.pack(side="left", padx=5)
        
    def setup_logging(self):
        """设置日志记录"""
        self.logger = logging.getLogger("StockSetter")
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
        
    def validate_inputs(self) -> bool:
        """验证输入参数
        
        Returns:
            验证是否通过
        """
        try:
            stock_num = int(self.stock_var.get())
            if stock_num <= 0:
                messagebox.showerror("错误", "库存数量必须大于0")
                return False
        except ValueError:
            messagebox.showerror("错误", "库存数量必须是数字")
            return False
            
        try:
            thread_num = int(self.thread_var.get())
            if thread_num <= 0 or thread_num > 20:
                messagebox.showerror("错误", "线程数必须在1-20之间")
                return False
        except ValueError:
            messagebox.showerror("错误", "线程数必须是数字")
            return False
            
        return True
        
    def start_setting(self):
        """开始设置库存流程"""
        try:
            # 验证输入
            if not self.validate_inputs():
                return
                
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置好卖家Cookie")
                return
                
            # 获取参数
            stock_num = int(self.stock_var.get())
            thread_num = int(self.thread_var.get())
                
            # 更新按钮状态
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # 设置停止标志
            self._stop_flag = False
            
            # 创建爬虫实例
            self.crawler = StockBatchSetter(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress,
                stop_flag_callback=lambda: self._stop_flag
            )
            
            # 启动处理线程
            thread = threading.Thread(
                target=self.run_setting,
                args=(stock_num, thread_num)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"启动过程发生错误: {str(e)}")
            messagebox.showerror("错误", f"启动失败: {str(e)}")
            
    def run_setting(self, stock_num: int, thread_num: int):
        """运行设置库存流程"""
        try:
            self.logger.info(f"开始批量设置库存，库存数量: {stock_num}，线程数: {thread_num}")
            self.update_progress(0, 0)
            
            result = self.crawler.batch_set_stock(stock_num, thread_num)
            
            # 显示结果
            if result:
                success = result.get("success", 0)
                failed = result.get("failed", 0)
                total = result.get("total", 0)
                self.logger.info(f"批量设置库存完成! 成功: {success}, 失败: {failed}, 总计: {total}")
                
                if failed == 0:
                    messagebox.showinfo("完成", f"批量设置库存成功完成！\n成功: {success} 个商品")
                else:
                    messagebox.showwarning("完成", f"批量设置库存完成，但有部分失败！\n成功: {success}, 失败: {failed}")
            else:
                self.logger.info("批量设置库存任务结束。")
            
        except Exception as e:
            self.logger.error(f"处理过程发生错误: {str(e)}")
            
        finally:
            # 恢复按钮状态
            self.after(0, lambda: self.start_button.configure(state="normal"))
            self.after(0, lambda: self.stop_button.configure(state="disabled"))
            
    def stop_setting(self):
        """停止设置库存流程"""
        self._stop_flag = True
        self.logger.info("用户请求停止设置库存")
        messagebox.showinfo("提示", "正在停止设置库存，请稍候...")
        
    def clear_log(self):
        """清空日志"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
        self.logger.info("日志已清空")
        
    def update_progress(self, current: int, total: int):
        """更新进度条
        
        Args:
            current: 当前处理数量
            total: 总数量
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{current}/{total}")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="准备中...")
        self.update_idletasks() 