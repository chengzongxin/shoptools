import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import logging
import os
from datetime import datetime
from .crawler import PriceReviewCrawler, PriceReviewSuggestion
from ..config.global_config_manager import GlobalConfigManager
from ..system_config.config import SystemConfig
from ..config.config import category_config
from ..network.event_manager import EventManager

class PriceReviewTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 初始化默认值
        self.config = SystemConfig()
        self.global_config = GlobalConfigManager()
        self.current_data = []  # 存储当前获取的数据
        
        # 初始化停止标志
        self._stop_flag = False
        
        # 初始化事件管理器并订阅403错误事件
        self.event_manager = EventManager()
        self.event_manager.subscribe("config_error", self._handle_config_error)
        
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
        main_frame.rowconfigure(2, weight=1)
        
    def create_input_fields(self, parent):
        """创建输入字段"""
        # 创建一个子框架来容纳输入字段
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # 线程数设置
        ttk.Label(input_frame, text="并发线程数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.thread_var = tk.StringVar(value="5")
        self.thread_entry = ttk.Entry(input_frame, textvariable=self.thread_var, width=10)
        self.thread_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(input_frame, text="(建议1-10)").grid(row=0, column=2, sticky=tk.W)
        
        # 价格低于底线时的处理方式
        ttk.Label(input_frame, text="价格低于底线时:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.rebargain_var = tk.BooleanVar(value=True)  # 默认使用重新调价
        self.rebargain_radio = ttk.Radiobutton(
            input_frame, 
            text="重新调价（当前价格-1元）", 
            variable=self.rebargain_var, 
            value=True
        )
        self.rebargain_radio.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 最多核价几轮输入控件
        # 创建标签，提示用户输入最多核价的轮数
        ttk.Label(input_frame, text="最多核价几轮:（选择重新调价时生效）").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        # 创建一个字符串变量用于存储用户输入的轮数，默认值为5
        max_review_rounds = self.global_config.get_config().get("max_review_rounds", 5)
        self.max_review_rounds_var = tk.StringVar(value=str(max_review_rounds))
        # 创建输入框，让用户输入轮数
        self.max_review_rounds_entry = ttk.Entry(input_frame, textvariable=self.max_review_rounds_var, width=10)
        self.max_review_rounds_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        # 输入后，实时保存到全局配置
        def save_max_review_rounds(event):
            try:
                max_review_rounds = int(self.max_review_rounds_var.get())
                self.global_config.update_max_review_rounds(max_review_rounds)
            except ValueError:
                messagebox.showerror("错误", "最多核价几轮必须是数字")
        self.max_review_rounds_entry.bind("<KeyRelease>", save_max_review_rounds)
        
        self.reject_radio = ttk.Radiobutton(
            input_frame, 
            text="直接拒绝", 
            variable=self.rebargain_var, 
            value=False
        )
        self.reject_radio.grid(row=1, column=3, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        
        
        # 价格底线设置按钮
        self.thresholds_button = ttk.Button(
            input_frame,
            text="价格底线设置",
            command=self.open_thresholds_editor
        )
        self.thresholds_button.grid(row=2, column=2, sticky=tk.W, padx=(20, 0), pady=(10, 0))

        
        # 配置父框架的网格权重
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        
    def create_progress_bar(self, parent):
        """创建进度条"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.progress_label = ttk.Label(parent, text="0/0")
        self.progress_label.grid(row=1, column=2, sticky=tk.W, padx=5)
        
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
        
        # 批量处理按钮
        self.batch_button = ttk.Button(
            button_frame,
            text="开始批量核价",
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
        self.logger = logging.getLogger('price_review')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        # 添加文件处理器
        log_file = os.path.join(self.log_dir, f'price_review_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # 添加一个初始日志
        self.logger.info("核价管理工具已初始化")
        self.logger.info(f"日志文件保存在: {log_file}")
        
        # 初始化时刷新类别配置缓存
        try:
            category_config.refresh_cache()
            self.logger.info("已加载外部价格底线配置（如存在）")
        except Exception as e:
            self.logger.warning(f"加载外部价格底线配置失败：{str(e)}")
        
    def log_price_review(self, product_id: int, ext_code: str, suggestion: PriceReviewSuggestion, action: str, success: bool, message: str):
        """记录核价操作
        
        Args:
            product_id: 商品ID
            ext_code: 商品货号
            suggestion: 核价建议
            action: 操作类型（同意/拒绝）
            success: 是否成功
            message: 处理结果说明
        """
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product_id': product_id,
            'ext_code': ext_code,
            'current_price': suggestion.supplyPrice / 100,
            'suggest_price': suggestion.suggestSupplyPrice / 100,
            'action': action,
            'success': success,
            'message': message
        }
        
        # 记录到日志文件
        self.logger.info(f"核价操作: {json.dumps(log_entry, ensure_ascii=False)}")
            
    def _handle_config_error(self, **kwargs):
        """
        处理配置错误事件（403错误）
        当网络请求发生403错误时，这个方法会被自动调用
        
        参数:
            error_code: 错误代码（403）
            error_message: 错误消息
            request_type: 请求类型（GET/POST/PUT/DELETE）
        """
        error_code = kwargs.get('error_code', 'Unknown')
        request_type = kwargs.get('request_type', 'Unknown')
        
        # 设置停止标志，复用现有的停止机制
        self._stop_flag = True
        
        # 记录日志
        self.logger.error("=" * 50)
        self.logger.error("⚠️  检测到配置错误，自动停止任务！")
        self.logger.error(f"错误代码: {error_code}")
        self.logger.error(f"请求类型: {request_type}")
        self.logger.error("请前往'系统配置'页面检查Cookie和MallID设置")
        self.logger.error("=" * 50)
    
    def stop_crawling(self):
        """停止爬取"""
        self._stop_flag = True
        self.logger.info("=" * 50)
        self.logger.info("用户点击停止按钮 - 正在停止任务...")
        self.logger.info("正在取消未完成的任务，请稍候...")
        self.logger.info("=" * 50)

    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        
    def update_product_list(self):
        """更新商品列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加新数据
        for item in self.current_data:
            created_at = datetime.fromtimestamp(item['productCreatedAt']/1000).strftime('%Y-%m-%d %H:%M:%S')
            self.tree.insert('', 'end', values=(
                item['productId'],
                item['productName'],
                item['supplierPrice'],
                item['buyerName'],
                created_at,
                "待核价"
            ))

    def start_batch_processing(self):
        """开始批量处理核价"""
        try:
            # 获取线程数
            try:
                thread_num = int(self.thread_var.get())
                if thread_num <= 0 or thread_num > 20:
                    messagebox.showerror("错误", "线程数必须在1-20之间")
                    return
            except ValueError:
                messagebox.showerror("错误", "线程数必须是数字")
                return

            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            if not cookie:
                messagebox.showerror("错误", "请先在系统配置中设置Cookie")
                return

            # 显示确认对话框
            if not messagebox.askyesno("确认", f"确定要批量处理所有待核价商品吗？"):
                return

            # 禁用按钮
            self.batch_button.config(state='disabled')
            self.stop_button.config(state='normal')

            # 清空进度条
            self.progress_var.set(0)
            self.progress_label.config(text="0/0")

            # 设置停止标志
            self._stop_flag = False

            # 创建爬虫实例
            self.crawler = PriceReviewCrawler(
                cookie=cookie,
                logger=self.logger,
                progress_callback=self.update_progress_mt,
                stop_flag_callback=lambda: self._stop_flag
            )

            # 在新线程中运行批量处理
            self.crawler_thread = threading.Thread(
                target=self.run_batch_processing_mt,
                args=(thread_num,)
            )
            self.crawler_thread.start()

        except Exception as e:
            self.logger.error(f"启动批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"启动批量处理失败: {str(e)}")

    def run_batch_processing_mt(self, thread_num):
        """运行多线程批量处理"""
        try:
            # 获取重新调价设置
            use_rebargain = self.rebargain_var.get()
            max_review_rounds = int(self.max_review_rounds_var.get())
            # 获取最多核价几轮
            results = self.crawler.batch_process_price_reviews_mt(thread_num, use_rebargain, max_review_rounds)
            # 统计处理结果
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
            # 显示处理结果
            message = f"批量处理完成\n成功: {success_count} 个\n失败: {fail_count} 个"
            self.logger.info(message)
            messagebox.showinfo("完成", message)
        except Exception as e:
            self.logger.error(f"批量处理失败: {str(e)}")
            messagebox.showerror("错误", f"批量处理失败: {str(e)}")
        finally:
            self.batch_button.config(state='normal')
            self.stop_button.config(state='disabled')

    def update_progress_mt(self, current, total):
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{current}/{total}")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="0/0")
        self.update_idletasks() 

    # ============== 价格底线配置 ==============

    def open_thresholds_editor(self):
        """打开价格底线编辑器对话框"""
        top = tk.Toplevel(self)
        top.title("价格底线设置")
        top.geometry("500x800")

        container = ttk.Frame(top, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(container, text="商品类别 → 底线价格(元)", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        # 创建滚动框架
        canvas = tk.Canvas(container, height=400)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))

        # 表头
        ttk.Label(scrollable_frame, text="类别名称", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Label(scrollable_frame, text="类别ID", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(0, 10), pady=5)
        ttk.Label(scrollable_frame, text="底线价格(元)", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=5)

        # 获取所有类别配置
        categories = category_config.get_categories(enabled_only=True)
        category_vars = []  # (category_dict, price_var)
        
        row_index = 1
        for category in categories:
            name = category.get("name", "")
            cate_id = category.get("cate_id", 0)
            price_threshold = category.get("price_threshold", 0.0)
            
            # 类别名称
            ttk.Label(scrollable_frame, text=name, width=20).grid(row=row_index, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            # 类别ID
            ttk.Label(scrollable_frame, text=str(cate_id), width=10).grid(row=row_index, column=1, sticky=tk.W, padx=(0, 10), pady=2)
            
            # 价格输入框
            price_var = tk.StringVar(value=str(price_threshold))
            ttk.Entry(scrollable_frame, textvariable=price_var, width=15).grid(row=row_index, column=2, sticky=tk.W, padx=(0, 10), pady=2)
            
            category_vars.append((category, price_var))
            row_index += 1

        # 配置网格权重
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # 操作按钮框架
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        def on_save():
            """保存价格底线配置"""
            try:
                # 更新所有类别的价格阈值
                updated_categories = []
                for category, price_var in category_vars:
                    try:
                        new_price = float(price_var.get().strip())
                        # 创建更新后的类别数据
                        updated_category = category.copy()
                        updated_category["price_threshold"] = new_price
                        updated_categories.append(updated_category)
                    except ValueError:
                        messagebox.showerror("错误", f"类别 '{category.get('name', '')}' 的价格必须是数字")
                        return
                
                # 保存到配置文件
                config_data = {
                    "categories": updated_categories,
                    "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 直接写入配置文件
                with open(category_config.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                # 刷新缓存
                category_config.refresh_cache()
                
                messagebox.showinfo("成功", "价格底线配置已保存")
                self.logger.info("价格底线配置已更新")
                top.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
                self.logger.error(f"保存价格底线配置失败: {str(e)}")

        def on_refresh():
            """刷新配置"""
            try:
                category_config.refresh_cache()
                messagebox.showinfo("成功", "配置已刷新")
                top.destroy()
                # 重新打开对话框
                self.open_thresholds_editor()
            except Exception as e:
                messagebox.showerror("错误", f"刷新失败：{str(e)}")

        ttk.Button(btn_frame, text="保存", command=on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=on_refresh).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=top.destroy).pack(side=tk.RIGHT, padx=5)