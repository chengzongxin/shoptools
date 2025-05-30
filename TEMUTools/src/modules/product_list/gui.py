import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import logging
import csv
from datetime import datetime
from .crawler import ProductListCrawler

class ProductListTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 初始化默认值
        self.last_cookie = ''
        self.last_anti_content = ''
        self.last_mallid = '634418223796259'
        self.last_pages = '2'
        self.last_page_size = '20'
        self.current_data = []  # 存储当前获取的数据
        
        # 加载保存的参数
        self.load_last_params()
        
        # 设置UI
        self.setup_ui()
        
        # 绑定变量变化事件
        self.bind_variable_changes()
        
    def bind_variable_changes(self):
        """绑定变量变化事件，实现自动保存"""
        self.pages_var.trace_add('write', lambda *args: self.auto_save())
        self.page_size_var.trace_add('write', lambda *args: self.auto_save())
        self.cookie_var.trace_add('write', lambda *args: self.auto_save())
        self.anti_content_var.trace_add('write', lambda *args: self.auto_save())
        self.mallid_var.trace_add('write', lambda *args: self.auto_save())
        
    def auto_save(self):
        """自动保存配置"""
        try:
            self.save_params()
        except Exception as e:
            logging.error(f"自动保存配置失败: {str(e)}")

    def setup_ui(self):
        """设置UI界面"""
        # 创建输入框和标签
        self.create_input_fields()
        
        # 创建Cookie输入区域
        self.create_cookie_input()
        
        # 创建进度条
        self.create_progress_bar()
        
        # 创建日志显示区域
        self.create_log_area()
        
        # 创建按钮
        self.create_buttons()
        
        # 配置日志处理器
        self.setup_logging()
        
    def load_last_params(self):
        """加载上次保存的参数"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_cookie = config.get('cookie', '')
                    self.last_anti_content = config.get('anti_content', '')
                    self.last_mallid = config.get('mallid', '634418223796259')
                    self.last_pages = config.get('pages', '2')
                    self.last_page_size = config.get('page_size', '20')
                logging.info("已加载上次保存的配置")
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            # 使用默认值
            self.last_cookie = ''
            self.last_anti_content = ''
            self.last_mallid = '634418223796259'
            self.last_pages = '2'
            self.last_page_size = '20'
            logging.info("使用默认配置")

    def save_params(self):
        """保存当前参数"""
        try:
            config = {
                'cookie': self.cookie_var.get().strip(),
                'anti_content': self.anti_content_var.get().strip(),
                'mallid': self.mallid_var.get().strip(),
                'pages': self.pages_var.get().strip(),
                'page_size': self.page_size_var.get().strip()
            }
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logging.info("配置已保存")
        except Exception as e:
            logging.error(f"保存配置文件失败: {str(e)}")
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def create_input_fields(self):
        """创建输入字段"""
        # 页数输入
        ttk.Label(self, text="获取页数:").grid(row=0, column=0, sticky=tk.W)
        self.pages_var = tk.StringVar(value=self.last_pages)
        self.pages_entry = ttk.Entry(self, textvariable=self.pages_var, width=10)
        self.pages_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 每页数据量输入
        ttk.Label(self, text="每页数据量:").grid(row=1, column=0, sticky=tk.W)
        self.page_size_var = tk.StringVar(value=self.last_page_size)
        self.page_size_entry = ttk.Entry(self, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=1, column=1, sticky=tk.W)
        
    def create_cookie_input(self):
        """创建Cookie输入区域"""
        # Cookie输入框架
        cookie_frame = ttk.LabelFrame(self, text="请求头设置", padding="5")
        cookie_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Cookie输入
        ttk.Label(cookie_frame, text="Cookie:").grid(row=0, column=0, sticky=tk.W)
        self.cookie_var = tk.StringVar(value=self.last_cookie)
        self.cookie_entry = ttk.Entry(cookie_frame, textvariable=self.cookie_var, width=80)
        self.cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Anti-content输入
        ttk.Label(cookie_frame, text="Anti-content:").grid(row=1, column=0, sticky=tk.W)
        self.anti_content_var = tk.StringVar(value=self.last_anti_content)
        self.anti_content_entry = ttk.Entry(cookie_frame, textvariable=self.anti_content_var, width=80)
        self.anti_content_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # MallID输入
        ttk.Label(cookie_frame, text="MallID:").grid(row=2, column=0, sticky=tk.W)
        self.mallid_var = tk.StringVar(value=self.last_mallid)
        self.mallid_entry = ttk.Entry(cookie_frame, textvariable=self.mallid_var, width=80)
        self.mallid_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 添加说明标签
        ttk.Label(
            cookie_frame, 
            text="请从浏览器开发者工具中复制Cookie、Anti-content和MallID值",
            font=("Arial", 8)
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
        
    def create_progress_bar(self):
        """创建进度条"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
    def create_log_area(self):
        """创建日志显示区域"""
        # 创建日志文本框
        self.log_text = tk.Text(self, height=15, width=80)
        self.log_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def create_buttons(self):
        """创建按钮"""
        # 创建按钮框架
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 开始按钮
        self.start_button = ttk.Button(
            button_frame, 
            text="开始爬取",
            command=self.start_crawling
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_crawling,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 保存配置按钮
        self.save_button = ttk.Button(
            button_frame,
            text="保存配置",
            command=self.save_params
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # 导出数据按钮
        self.export_button = ttk.Button(
            button_frame,
            text="导出数据",
            command=self.export_data,
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # 配置日志
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(text_handler)
        
    def start_crawling(self):
        """开始爬取数据"""
        try:
            # 获取输入值
            pages = int(self.pages_var.get())
            page_size = int(self.page_size_var.get())
            cookie = self.cookie_var.get().strip()
            anti_content = self.anti_content_var.get().strip()
            mallid = self.mallid_var.get().strip()
            
            if pages <= 0 or page_size <= 0:
                messagebox.showerror("错误", "页数和每页数据量必须大于0")
                return
                
            if not cookie:
                messagebox.showerror("错误", "请输入Cookie值")
                return
                
            if not anti_content:
                messagebox.showerror("错误", "请输入Anti-content值")
                return
                
            if not mallid:
                messagebox.showerror("错误", "请输入MallID值")
                return
                
            # 保存当前参数
            self.save_params()
            
            # 禁用输入和开始按钮
            self.pages_entry.configure(state='disabled')
            self.page_size_entry.configure(state='disabled')
            self.cookie_entry.configure(state='disabled')
            self.anti_content_entry.configure(state='disabled')
            self.mallid_entry.configure(state='disabled')
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            # 清空日志
            self.log_text.delete(1.0, tk.END)
            
            # 在新线程中运行爬虫
            self.crawler_thread = threading.Thread(
                target=self.run_crawler,
                args=(pages, page_size, cookie, anti_content, mallid)
            )
            self.crawler_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            
    def run_crawler(self, pages, page_size, cookie, anti_content, mallid):
        """运行爬虫"""
        try:
            crawler = ProductListCrawler()
            crawler.page_size = page_size
            
            # 更新请求头
            crawler.headers['cookie'] = cookie
            crawler.headers['anti-content'] = anti_content
            crawler.headers['mallid'] = mallid
            
            # 获取数据
            logging.info(f"开始获取商品列表数据，计划获取 {pages} 页...")
            all_data = crawler.get_all_data(max_pages=pages)
            
            if all_data:
                self.current_data = all_data  # 保存当前数据
                logging.info(f"共获取到 {len(all_data)} 条数据")
                # 启用导出按钮
                self.export_button.configure(state='normal')
            else:
                self.current_data = []  # 清空当前数据
                logging.warning("未获取到任何数据")
                # 禁用导出按钮
                self.export_button.configure(state='disabled')
                
        except Exception as e:
            self.current_data = []  # 清空当前数据
            logging.error(f"程序执行出错: {str(e)}")
            # 禁用导出按钮
            self.export_button.configure(state='disabled')
        finally:
            # 恢复界面状态
            self.after(0, self.reset_ui)
            
    def stop_crawling(self):
        """停止爬取"""
        self.stop_button.configure(state='disabled')
        logging.info("正在停止爬取...")
        
    def reset_ui(self):
        """重置界面状态"""
        self.pages_entry.configure(state='normal')
        self.page_size_entry.configure(state='normal')
        self.cookie_entry.configure(state='normal')
        self.anti_content_entry.configure(state='normal')
        self.mallid_entry.configure(state='normal')
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        # 根据是否有数据来设置导出按钮状态
        self.export_button.configure(state='normal' if self.current_data else 'disabled')

    def export_data(self):
        """导出数据到CSV文件"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        try:
            # 获取保存路径
            default_filename = f"商品列表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv")],
                initialfile=default_filename
            )
            
            if not file_path:  # 用户取消保存
                return
                
            # 写入CSV文件
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.current_data[0].keys())
                writer.writeheader()
                writer.writerows(self.current_data)
                
            logging.info(f"数据已导出到: {file_path}")
            messagebox.showinfo("成功", "数据导出成功！")
            
        except Exception as e:
            error_msg = f"导出数据失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg) 