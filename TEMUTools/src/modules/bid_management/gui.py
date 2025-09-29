"""
竞价管理模块GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
import os
from datetime import datetime
from typing import List, Optional
from .crawler import BidManagementCrawler
from .models import BidResult
from ..system_config.config import SystemConfig


class BidManagementTab(ttk.Frame):
    """竞价管理标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.config = SystemConfig()
        self.crawler: Optional[BidManagementCrawler] = None
        self.current_results: List[BidResult] = []
        self.is_processing = False
        
        # 创建日志目录
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建配置区域
        self.create_config_section(main_frame)
        
        # 创建控制按钮区域
        self.create_control_section(main_frame)
        
        # 创建进度条
        self.create_progress_section(main_frame)
        
        # 创建日志显示区域
        self.create_log_section(main_frame)
        
        # 创建结果统计区域
        self.create_stats_section(main_frame)
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 日志区域可扩展
        
    def create_config_section(self, parent):
        """创建配置区域"""
        config_frame = ttk.LabelFrame(parent, text="竞价配置", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 减价金额设置
        ttk.Label(config_frame, text="减价金额(元):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # 从配置文件加载默认值
        from ..config.config import bid_config
        default_reduction = bid_config.get_bid_reduction()
        self.bid_reduction_var = tk.StringVar(value=str(default_reduction))
        bid_reduction_entry = ttk.Entry(config_frame, textvariable=self.bid_reduction_var, width=10)
        bid_reduction_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # 说明文字
        ttk.Label(config_frame, text="(竞价时将在最低价基础上减少此金额)", 
                 foreground="gray").grid(row=0, column=2, sticky=tk.W)
        
        # 价格阈值检查开关
        self.enable_threshold_check_var = tk.BooleanVar(value=bid_config.is_price_threshold_check_enabled())
        threshold_check = ttk.Checkbutton(
            config_frame, 
            text="启用价格底线检查", 
            variable=self.enable_threshold_check_var
        )
        threshold_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 价格阈值说明
        ttk.Label(config_frame, text="(启用后将根据商品类别检查价格底线，低于底线不参与竞价)", 
                 foreground="gray").grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
        
        config_frame.columnconfigure(2, weight=1)
        
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, pady=(0, 10))
        
        # 开始竞价按钮
        self.start_button = ttk.Button(
            control_frame, 
            text="开始自动竞价", 
            command=self.start_bidding,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(
            control_frame,
            text="停止处理",
            command=self.stop_processing,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        self.clear_button = ttk.Button(
            control_frame,
            text="清空日志",
            command=self.clear_log
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 导出结果按钮
        self.export_button = ttk.Button(
            control_frame,
            text="导出结果",
            command=self.export_results,
            state='disabled'
        )
        self.export_button.pack(side=tk.LEFT)
        
    def create_progress_section(self, parent):
        """创建进度条区域"""
        progress_frame = ttk.LabelFrame(parent, text="处理进度", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 进度标签
        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        progress_frame.columnconfigure(0, weight=1)
        
    def create_log_section(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            wrap=tk.WORD,
            state='disabled'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def create_stats_section(self, parent):
        """创建结果统计区域"""
        stats_frame = ttk.LabelFrame(parent, text="处理统计", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        # 统计标签
        self.stats_label = ttk.Label(
            stats_frame, 
            text="总处理: 0 | 成功: 0 | 实际竞价: 0 | 无需竞价: 0 | 失败: 0"
        )
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        stats_frame.columnconfigure(0, weight=1)
        
    def setup_logging(self):
        """设置日志"""
        # 创建日志文件
        log_file = os.path.join(self.log_dir, f'bid_management_{datetime.now().strftime("%Y%m%d")}.log')
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 创建专用日志记录器
        self.logger = logging.getLogger('bid_management')
        self.logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        
        # 防止传播到根日志记录器
        self.logger.propagate = False
        
    def log_message(self, message: str, level: str = "INFO"):
        """在GUI中显示日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # 在GUI中显示
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        # 写入日志文件
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
            
        # 更新界面
        self.update_idletasks()
        
    def update_progress(self, message: str, current: int = None, total: int = None):
        """更新进度"""
        self.progress_label.config(text=message)
        
        if current is not None and total is not None and total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        self.log_message(message)
        
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
    def update_stats(self):
        """更新统计信息"""
        if not self.current_results:
            self.stats_label.config(text="总处理: 0 | 成功: 0 | 实际竞价: 0 | 无需竞价: 0 | 失败: 0")
            return
            
        total = len(self.current_results)
        success = sum(1 for r in self.current_results if r.success)
        bid_count = sum(1 for r in self.current_results if r.needBid and r.success)
        no_bid_count = sum(1 for r in self.current_results if not r.needBid and r.success)
        failed = total - success
        
        stats_text = f"总处理: {total} | 成功: {success} | 实际竞价: {bid_count} | 无需竞价: {no_bid_count} | 失败: {failed}"
        self.stats_label.config(text=stats_text)
        
    def start_bidding(self):
        """开始竞价处理"""
        if self.is_processing:
            messagebox.showwarning("警告", "竞价处理正在进行中，请等待完成")
            return
            
        # 验证减价金额
        try:
            bid_reduction = float(self.bid_reduction_var.get())
            if bid_reduction < 0:
                messagebox.showerror("错误", "减价金额不能为负数")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的减价金额")
            return
            
        # 获取价格阈值检查设置
        enable_threshold_check = self.enable_threshold_check_var.get()
        
        # 保存配置到配置文件
        from ..config.config import bid_config
        bid_config.set_bid_reduction(bid_reduction)
        config_data = bid_config._load_config()
        config_data["enable_price_threshold_check"] = enable_threshold_check
        bid_config.save_config(config_data)
            
        # 确认开始处理
        if not messagebox.askyesno("确认", "确定要开始自动竞价处理吗？\n\n这将自动处理所有待确认邀约和竞价失败的商品。"):
            return
            
        # 更新UI状态
        self.is_processing = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.export_button.config(state='disabled')
        
        # 清空之前的结果
        self.current_results.clear()
        self.update_stats()
        
        # 在后台线程中执行竞价处理
        threading.Thread(target=self._process_bids_thread, daemon=True).start()
        
    def _process_bids_thread(self):
        """在后台线程中处理竞价"""
        try:
            # 创建爬虫实例（配置会自动从配置文件加载）
            self.crawler = BidManagementCrawler(
                logger=self.logger,
                progress_callback=self.update_progress
            )
            
            self.log_message("开始竞价处理...")
            
            # 处理所有竞价
            results = self.crawler.process_all_bids()
            
            if not self.is_processing:  # 检查是否被停止
                self.log_message("竞价处理已停止", "WARNING")
                return
                
            # 保存结果
            self.current_results = results
            
            # 更新统计信息
            self.update_stats()
            
            # 显示完成消息
            success_count = sum(1 for r in results if r.success)
            bid_count = sum(1 for r in results if r.needBid and r.success)
            
            self.log_message(f"竞价处理完成！总计处理 {len(results)} 个商品，成功 {success_count} 个，实际竞价 {bid_count} 个")
            
            # 更新进度条
            self.progress_var.set(100)
            self.progress_label.config(text="处理完成")
            
        except Exception as e:
            self.log_message(f"竞价处理发生异常: {str(e)}", "ERROR")
            messagebox.showerror("错误", f"竞价处理失败：{str(e)}")
            
        finally:
            # 恢复UI状态
            self.is_processing = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
            if self.current_results:
                self.export_button.config(state='normal')
                
    def stop_processing(self):
        """停止处理"""
        if not self.is_processing:
            return
            
        if messagebox.askyesno("确认", "确定要停止竞价处理吗？"):
            self.is_processing = False
            self.log_message("正在停止竞价处理...", "WARNING")
            
    def export_results(self):
        """导出竞价结果"""
        if not self.current_results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
            
        from tkinter import filedialog
        import csv
        
        # 选择保存文件
        filename = filedialog.asksaveasfilename(
            title="保存竞价结果",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialname=f"bid_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    '商品ID', '商品名称', '竞价订单ID', '原价格', '竞价价格', 
                    '最低价格', '是否需要竞价', '处理结果', '消息'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.current_results:
                    writer.writerow({
                        '商品ID': result.productId,
                        '商品名称': result.productName,
                        '竞价订单ID': result.priceComparingOrderId,
                        '原价格': result.originalPrice,
                        '竞价价格': result.bidPrice,
                        '最低价格': result.minPrice,
                        '是否需要竞价': '是' if result.needBid else '否',
                        '处理结果': '成功' if result.success else '失败',
                        '消息': result.message
                    })
                    
            self.log_message(f"结果已导出到: {filename}")
            messagebox.showinfo("成功", f"竞价结果已导出到:\n{filename}")
            
        except Exception as e:
            self.log_message(f"导出结果失败: {str(e)}", "ERROR")
            messagebox.showerror("错误", f"导出结果失败：{str(e)}")
