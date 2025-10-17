import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from datetime import datetime
from .crawler import CertChecker


class CertCheckerGUI:
    """资质排查GUI界面类"""
    
    def __init__(self, parent_notebook):
        """初始化GUI
        
        Args:
            parent_notebook: 父级Notebook组件
        """
        # 创建标签页
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text='资质排查')
        
        # 设置日志
        self.setup_logger()
        
        # 停止标志
        self.stop_flag = False
        
        # 创建UI组件
        self.create_widgets()
        
    def setup_logger(self):
        """设置日志记录器"""
        import os
        self.logger = logging.getLogger('CertChecker')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            
            # 确保日志目录存在
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 文件handler
            log_file = os.path.join(log_dir, f'cert_checker_{datetime.now().strftime("%Y%m%d")}.log')
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
            # 控制台handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
    
    def create_widgets(self):
        """创建UI组件"""
        # 主容器
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
#         # 标题区域
#         title_frame = ttk.Frame(main_container)
#         title_frame.pack(fill=tk.X, pady=(0, 20))
        
#         title_label = ttk.Label(
#             title_frame,
#             text="资质排查 - 自动下架需要资质的商品",
#             font=("微软雅黑", 14, "bold")
#         )
#         title_label.pack()
        
#         # 说明区域
#         info_frame = ttk.LabelFrame(main_container, text="功能说明", padding="10")
#         info_frame.pack(fill=tk.X, pady=(0, 20))
        
#         info_text = """
# 📋 功能说明:
#   1. 自动查询所有资质类型（排除GCC资质）
#   2. 查询所有触发资质要求的商品
#   3. 批量将这些商品的库存设为0（下架处理）

# ⚠️ 注意事项:
#   • 本功能会自动排除GCC（ID=28）资质
#   • 如果资质类型超过500个，会自动分批查询
#   • 下架操作不可逆，请谨慎使用
#   • 建议在执行前做好数据备份
#         """
        
#         info_label = ttk.Label(
#             info_frame,
#             text=info_text,
#             justify=tk.LEFT,
#             foreground="#555"
#         )
#         info_label.pack(anchor=tk.W)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_container, text="执行设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 并发线程数设置
        thread_frame = ttk.Frame(settings_frame)
        thread_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(thread_frame, text="并发线程数:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.thread_count_var = tk.IntVar(value=5)
        thread_spinbox = ttk.Spinbox(
            thread_frame,
            from_=1,
            to=10,
            textvariable=self.thread_count_var,
            width=10
        )
        thread_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(
            thread_frame,
            text="(建议1-10之间，数值越大速度越快但可能被限流)",
            foreground="#666"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 开始执行按钮
        self.start_button = ttk.Button(
            button_frame,
            text="🚀 开始执行资质排查",
            command=self.start_check,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹ 停止",
            command=self.stop_check,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_container, text="执行进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 进度标签
        self.progress_label = ttk.Label(
            progress_frame,
            text="等待开始...",
            foreground="#666"
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 日志文本框
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=15,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # 添加日志handler到文本框
        self.add_text_handler()
    
    def add_text_handler(self):
        """添加文本框日志handler"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                
                # 使用after方法在主线程中更新UI
                self.text_widget.after(0, append)
        
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        self.logger.addHandler(text_handler)
    
    def update_progress(self, current, total):
        """更新进度
        
        Args:
            current: 当前进度
            total: 总数
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(
                text=f"正在处理: {current}/{total} ({percentage:.1f}%)"
            )
    
    def check_stop_flag(self):
        """检查停止标志"""
        return self.stop_flag
    
    def start_check(self):
        """开始执行资质排查"""
        # 确认对话框
        result = messagebox.askyesno(
            "确认执行",
            "此操作将会:\n\n"
            "1. 查询所有触发资质要求的商品（排除GCC）\n"
            "2. 将这些商品的库存全部设为0（下架）\n\n",
            icon='warning'
        )
        
        if not result:
            return
        
        # 重置停止标志
        self.stop_flag = False
        
        # 更新UI状态
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_label.config(text="正在初始化...")
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中执行
        thread = threading.Thread(target=self.run_check, daemon=True)
        thread.start()
    
    def stop_check(self):
        """停止执行"""
        self.stop_flag = True
        self.logger.info("正在停止，请稍候...")
        self.stop_button.config(state=tk.DISABLED)
    
    def run_check(self):
        """执行资质排查（在后台线程中运行）"""
        try:
            self.logger.info("="*60)
            self.logger.info("开始执行资质排查任务")
            self.logger.info("="*60)
            
            # 创建爬虫实例
            crawler = CertChecker(
                logger=self.logger,
                progress_callback=self.update_progress,
                stop_flag_callback=self.check_stop_flag
            )
            
            # 获取并发线程数
            max_workers = self.thread_count_var.get()
            
            # 执行批量下架
            result = crawler.batch_set_stock_to_zero(max_workers=max_workers)
            
            # 显示结果
            if self.stop_flag:
                messagebox.showinfo(
                    "任务已停止",
                    f"任务已被手动停止\n\n"
                    f"已处理: {result['success'] + result['failed']}/{result['total']} 个商品"
                )
            else:
                messagebox.showinfo(
                    "执行完成",
                    f"资质排查任务已完成！\n\n"
                    f"成功: {result['success']} 个商品\n"
                    f"失败: {result['failed']} 个商品\n"
                    f"总计: {result['total']} 个商品"
                )
            
        except Exception as e:
            self.logger.error(f"执行资质排查时发生异常: {str(e)}")
            messagebox.showerror("执行失败", f"执行过程中发生错误:\n{str(e)}")
            
        finally:
            # 恢复UI状态
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_label.config(text="执行完成")

