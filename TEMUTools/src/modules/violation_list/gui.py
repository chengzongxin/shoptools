import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from .crawler import ViolationListCrawler
from .excel_exporter import ViolationListExcelExporter
import logging

logger = logging.getLogger(__name__)

class ViolationListTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.crawler = ViolationListCrawler()
        self.excel_exporter = ViolationListExcelExporter()
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'violation_config.json')
        self.setup_ui()
        self.load_config()
        self.setup_logging()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建输入字段
        self.create_input_fields()
        
        # 创建Cookie输入区域
        self.create_cookie_input()
        
        # 创建日志显示区域
        self.create_log_area()
        
        # 创建按钮
        self.create_buttons()
        
        # 配置日志处理器
        self.setup_logging()
        
    def create_input_fields(self):
        """创建输入字段"""
        # 页数输入
        ttk.Label(self, text="获取页数:").grid(row=0, column=0, sticky=tk.W)
        self.start_page_var = tk.StringVar(value="1")
        self.start_page_entry = ttk.Entry(self, textvariable=self.start_page_var, width=10)
        self.start_page_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 每页数据量输入
        ttk.Label(self, text="每页数据量:").grid(row=1, column=0, sticky=tk.W)
        self.page_size_var = tk.StringVar(value="100")
        self.page_size_entry = ttk.Entry(self, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=1, column=1, sticky=tk.W)
        
    def create_cookie_input(self):
        """创建Cookie输入区域"""
        # Cookie输入框架
        cookie_frame = ttk.LabelFrame(self, text="请求头设置", padding="5")
        cookie_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Cookie输入
        ttk.Label(cookie_frame, text="Cookie:").grid(row=0, column=0, sticky=tk.W)
        self.cookie_entry = ttk.Entry(cookie_frame, width=80)
        self.cookie_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Anti-content输入
        ttk.Label(cookie_frame, text="Anti-content:").grid(row=1, column=0, sticky=tk.W)
        self.anti_content_entry = ttk.Entry(cookie_frame, width=80)
        self.anti_content_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # MallID输入
        ttk.Label(cookie_frame, text="MallID:").grid(row=2, column=0, sticky=tk.W)
        self.mallid_entry = ttk.Entry(cookie_frame, width=80)
        self.mallid_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 添加说明标签
        ttk.Label(
            cookie_frame, 
            text="请从浏览器开发者工具中复制Cookie、Anti-content和MallID值",
            font=("Arial", 8)
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
        
    def create_log_area(self):
        """创建日志显示区域"""
        # 创建日志文本框
        self.log_text = tk.Text(self, height=15, width=80)
        self.log_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def create_buttons(self):
        """创建按钮"""
        # 创建按钮框架
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 开始按钮
        self.start_button = ttk.Button(
            button_frame, 
            text="开始获取",
            command=self.start_crawling
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 导出Excel按钮
        self.export_button = ttk.Button(
            button_frame,
            text="导出Excel",
            command=self.export_to_excel,
            state='disabled'  # 初始状态为禁用
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # 保存配置按钮
        self.save_config_button = ttk.Button(
            button_frame,
            text="保存配置",
            command=self.save_config
        )
        self.save_config_button.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        self.clear_button = ttk.Button(
            button_frame,
            text="清空",
            command=self.clear_all
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 存储当前数据
        self.violation_data = []
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.cookie_entry.insert(0, config.get('cookie', ''))
                    self.anti_content_entry.insert(0, config.get('anti_content', ''))
                    self.mallid_entry.insert(0, config.get('mallid', ''))
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'cookie': self.cookie_entry.get().strip(),
                'anti_content': self.anti_content_entry.get().strip(),
                'mallid': self.mallid_entry.get().strip()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")
        
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
        
        # 移除所有现有的处理器
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 设置日志级别
        logger.setLevel(logging.INFO)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(text_handler)
        
        # 添加一个初始日志
        logger.info("违规商品列表工具已初始化")

    def start_crawling(self):
        """开始爬取数据"""
        # 获取配置
        cookie = self.cookie_entry.get().strip()
        anti_content = self.anti_content_entry.get().strip()
        mallid = self.mallid_entry.get().strip()
        
        # 验证配置
        if not all([cookie, anti_content, mallid]):
            messagebox.showerror("错误", "请填写完整的配置信息！")
            return
            
        # 获取分页设置
        try:
            start_page = int(self.start_page_var.get())
            page_size = int(self.page_size_var.get())
            
            if start_page < 1 or page_size < 1:
                messagebox.showerror("错误", "页码和页数必须大于0！")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
            return
        
        # 更新爬虫配置
        self.crawler.headers.update({
            "cookie": cookie,
            "anti-content": anti_content,
            "mallid": mallid
        })
        self.crawler.page_size = page_size
        
        try:
            # 禁用开始按钮，防止重复点击
            self.start_button.config(state='disabled')
            
            # 清空日志
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state='disabled')
            
            # 获取数据
            self.violation_data = self.crawler.get_all_data(max_pages=start_page)
            
            if not self.violation_data:
                logger.info("未获取到数据！请检查配置信息是否正确。")
                return
            
            # 启用导出按钮
            self.export_button.config(state='normal')
            
            # 在日志中显示成功信息
            logger.info(f"成功获取 {len(self.violation_data)} 条数据！")
            
        except Exception as e:
            logger.error(f"获取数据时发生错误：{str(e)}")
        finally:
            # 恢复开始按钮状态
            self.start_button.config(state='normal')
    
    def clear_all(self):
        """清空所有内容"""
        self.cookie_entry.delete(0, tk.END)
        self.anti_content_entry.delete(0, tk.END)
        self.mallid_entry.delete(0, tk.END)
        self.start_page_var.set("1")
        self.page_size_var.set("100")
        
        # 清空日志
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # 清空数据
        self.violation_data = []
        
        # 禁用导出按钮
        self.export_button.config(state='disabled')
    
    def fetch_data(self):
        """获取数据"""
        try:
            # 获取输入值
            cookie = self.cookie_entry.get().strip()
            anti_content = self.anti_content_entry.get().strip()
            mallid = self.mallid_entry.get().strip()
            start_page = int(self.start_page_var.get())
            max_pages = int(self.page_size_var.get())
            
            # 验证输入
            if not cookie:
                messagebox.showerror("错误", "请输入Cookie")
                return
            if not anti_content:
                messagebox.showerror("错误", "请输入Anti-Content")
                return
            if not mallid:
                messagebox.showerror("错误", "请输入MallID")
                return
            
            # 设置请求头
            self.crawler.headers.update({
                "cookie": cookie,
                "anti-content": anti_content,
                "mallid": mallid
            })
            
            # 清空现有数据
            self.clear_tree()
            
            # 获取数据
            self.violation_data = self.crawler.get_all_data(start_page, max_pages)
            
            if not self.violation_data:
                messagebox.showinfo("提示", "未获取到数据")
                return
            
            # 显示数据
            self.display_data(self.violation_data)
            
            # 启用导出按钮
            self.export_button.config(state='normal')
            
            messagebox.showinfo("成功", f"成功获取 {len(self.violation_data)} 条数据")
            
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的页码和页数")
        except Exception as e:
            logger.error(f"获取数据时出错: {str(e)}")
            messagebox.showerror("错误", f"获取数据时出错: {str(e)}")
    
    def display_data(self, data: list):
        """在表格中显示数据"""
        for product in data:
            # 获取处罚详情
            punish_details = product.get('punish_detail_list', [])
            if not punish_details:
                # 如果没有处罚详情，添加基本信息
                self.tree.insert('', 'end', values=(
                    product.get('goods_id', ''),
                    product.get('goods_name', ''),
                    product.get('leaf_reason_name', ''),
                    product.get('violation_desc', ''),
                    '', '', '', '', '', '',
                    self.excel_exporter.format_appeal_status(product.get('appeal_status', 0)),
                    '', ''
                ))
                continue
            
            # 处理每个处罚详情
            for detail in punish_details:
                # 获取违规详情
                illegal_details = detail.get('illegal_detail', [])
                illegal_desc = '; '.join([
                    f"{illegal.get('title', '')}: {illegal.get('value', '')}"
                    for illegal in illegal_details
                ])
                
                # 格式化时间戳
                start_time = self.excel_exporter.format_timestamp(detail.get('start_time'))
                end_time = self.excel_exporter.format_timestamp(detail.get('plan_end_time'))
                
                # 插入数据
                self.tree.insert('', 'end', values=(
                    product.get('goods_id', ''),
                    product.get('goods_name', ''),
                    product.get('leaf_reason_name', ''),
                    product.get('violation_desc', ''),
                    detail.get('punish_appeal_type', ''),
                    detail.get('punish_infect_desc', ''),
                    illegal_desc,
                    detail.get('rectification_suggestion', ''),
                    start_time,
                    end_time,
                    self.excel_exporter.format_appeal_status(detail.get('appeal_status', 0)),
                    detail.get('now_appeal_time', 0),
                    detail.get('max_appeal_time', 0)
                ))
    
    def export_to_excel(self):
        """导出数据到Excel"""
        if not self.violation_data:
            messagebox.showinfo("提示", "没有数据可导出")
            return
        
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"违规商品列表_{timestamp}.xlsx"
            
            # 获取保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:  # 用户取消选择
                return
            
            # 构建完整的文件路径
            file_path = os.path.join(save_dir, default_filename)
            
            # 导出数据
            if self.excel_exporter.export_to_excel(self.violation_data, file_path):
                messagebox.showinfo("成功", f"数据已成功导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出数据失败")
                
        except Exception as e:
            logger.error(f"导出Excel时出错: {str(e)}")
            messagebox.showerror("错误", f"导出Excel时出错: {str(e)}") 