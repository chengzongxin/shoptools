import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from typing import Optional
from .crawler import StockBatchSetter
from ..system_config.config import SystemConfig
from ..network.event_manager import EventManager

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
        self._stop_flag = False
        
        # 初始化事件管理器并订阅403错误事件
        self.event_manager = EventManager()
        self.event_manager.subscribe("config_error", self._handle_config_error)
        
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建参数设置区域
        param_frame = ttk.LabelFrame(main_frame, text="参数设置")
        param_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.create_param_area(param_frame)
        
        # 创建进度条
        progress_frame = ttk.LabelFrame(main_frame, text="处理进度")
        progress_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.create_progress_bar(progress_frame)
        
        # 创建日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志")
        log_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.create_log_area(log_frame)
        
        # 创建按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        self.create_buttons(button_frame)

        # 设置权重让界面能够自适应调整
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # 设置main_frame的权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 让日志区域（第2行）可以扩展
        
    def create_param_area(self, parent):
        """创建参数设置区域
        
        Args:
            parent: 父容器
        """
        # 天数设置
        days_frame = ttk.Frame(parent)
        days_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Label(days_frame, text="仅设置N天内创建的商品:").pack(side="left")
        self.days_var = tk.StringVar(value="5")
        self.days_entry = ttk.Entry(days_frame, textvariable=self.days_var, width=10)
        self.days_entry.pack(side="left", padx=5)
        ttk.Label(days_frame, text="(天)").pack(side="left")
        
        # 线程数设置
        thread_frame = ttk.Frame(parent)
        thread_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        self.progress_bar.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.progress_label = ttk.Label(parent, text="0/0")
        self.progress_label.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)

        parent.columnconfigure(0, weight=1)
        
    def create_log_area(self, parent):
        """创建日志区域
        
        Args:
            parent: 父容器
        """
        # 设置parent的grid权重，让子控件能够撑满
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建文本框
        self.log_text = tk.Text(parent)  # 移除固定的height=10限制
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # 添加滚动条，作为parent的子控件
        scrollbar = ttk.Scrollbar(parent, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        
        # 连接文本框和滚动条
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
        self.start_button.grid(row=0, column=0, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            parent,
            text="停止",
            command=self.stop_setting,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # 清空日志按钮
        self.clear_button = ttk.Button(
            parent,
            text="清空日志",
            command=self.clear_log
        )
        self.clear_button.grid(row=0, column=2, padx=5)
        
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
    
    def _handle_config_error(self, **kwargs):
        """处理配置错误事件（403错误）"""
        error_code = kwargs.get('error_code', 'Unknown')
        request_type = kwargs.get('request_type', 'Unknown')
        
        # 设置停止标志
        self._stop_flag = True
        
        # 记录日志
        self.logger.error("=" * 50)
        self.logger.error("⚠️  检测到配置错误，自动停止任务！")
        self.logger.error(f"错误代码: {error_code}")
        self.logger.error(f"请求类型: {request_type}")
        self.logger.error("请前往'系统配置'页面检查Cookie和MallID设置")
        self.logger.error("=" * 50)
        
    def validate_inputs(self) -> bool:
        """验证输入参数
        
        Returns:
            验证是否通过
        """
        try:
            days = int(self.days_var.get())
            if days <= 0:
                messagebox.showerror("错误", "天数必须大于0")
                return False
        except ValueError:
            messagebox.showerror("错误", "天数必须是数字")
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
            days = int(self.days_var.get())
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
                args=(days, thread_num)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"启动过程发生错误: {str(e)}")
            messagebox.showerror("错误", f"启动失败: {str(e)}")
            
    def run_setting(self, days: int, thread_num: int):
        """运行设置库存流程"""
        try:
            self.logger.info(f"开始批量设置库存，天数: {days}，线程数: {thread_num}")
            self.update_progress(0, 0)
            
            if self.crawler:
                result = self.crawler.batch_set_stock(max_workers=thread_num, days=days)
            else:
                self.logger.error("爬虫实例未初始化")
                return
            
            # 显示结果
            if result:
                success = result.get("success", 0)
                failed = result.get("failed", 0)
                total = result.get("total", 0)
                skipped = result.get("skipped", 0)
                self.logger.info(f"批量设置库存完成! 成功: {success}, 失败: {failed}, 跳过: {skipped}, 总计: {total}")
                
                if failed == 0 and total > 0:
                    messagebox.showinfo("完成", f"批量设置库存成功完成！\n成功: {success} 个商品\n跳过: {skipped} 个商品")
                elif total == 0:
                    messagebox.showwarning("完成", f"没有符合条件的商品（{days}天内创建）\n跳过: {skipped} 个商品")
                else:
                    messagebox.showwarning("完成", f"批量设置库存完成，但有部分失败！\n成功: {success}, 失败: {failed}, 跳过: {skipped}")
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