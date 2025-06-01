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
        
        # 设置配置文件路径
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        self.config_file = os.path.join(self.config_dir, 'violation_config.json')
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 初始化默认值
        self.last_pages = '1'
        self.last_page_size = '100'
        
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
        
        # 合并Excel按钮
        self.merge_button = ttk.Button(
            button_frame,
            text="合并Excel",
            command=self.merge_excel_files
        )
        self.merge_button.pack(side=tk.LEFT, padx=5)
        
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
                    self.start_page_var.set(config.get('pages', '1'))
                    self.page_size_var.set(config.get('page_size', '100'))
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            # 使用默认值
            self.start_page_var.set('1')
            self.page_size_var.set('100')
    
    def save_config(self):
        """保存配置"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'cookie': self.cookie_entry.get().strip(),
                'anti_content': self.anti_content_entry.get().strip(),
                'mallid': self.mallid_entry.get().strip(),
                'pages': self.start_page_var.get().strip(),
                'page_size': self.page_size_var.get().strip()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info("配置已保存")
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
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
        
        # 创建独立的logger
        self.logger = logging.getLogger('violation_list')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        # 添加一个初始日志
        self.logger.info("违规商品列表工具已初始化")

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
                self.logger.info("未获取到数据！请检查配置信息是否正确。")
                return
            
            # 启用导出按钮
            self.export_button.config(state='normal')
            
            # 在日志中显示成功信息
            self.logger.info(f"成功获取 {len(self.violation_data)} 条数据！")
            
        except Exception as e:
            self.logger.error(f"获取数据时发生错误：{str(e)}")
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
                self.logger.info(f"数据已成功导出到: {file_path}")
            else:
                self.logger.error("导出数据失败")
                
        except Exception as e:
            self.logger.error(f"导出Excel时出错: {str(e)}")
            messagebox.showerror("错误", f"导出Excel时出错: {str(e)}")

    def merge_excel_files(self):
        """合并违规列表和商品列表Excel文件"""
        try:
            # 选择违规列表Excel文件
            violation_file = filedialog.askopenfilename(
                title="选择违规列表Excel文件",
                filetypes=[("Excel文件", "*.xlsx")]
            )
            if not violation_file:
                return
                
            # 选择商品列表Excel文件
            product_file = filedialog.askopenfilename(
                title="选择商品列表Excel文件",
                filetypes=[("Excel文件", "*.xlsx")]
            )
            if not product_file:
                return
                
            # 选择保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:
                return
                
            # 生成输出文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(save_dir, f"合并数据_{timestamp}.xlsx")
            
            # 读取Excel文件
            from openpyxl import load_workbook
            
            # 读取违规列表
            violation_wb = load_workbook(violation_file)
            violation_ws = violation_wb.active
            
            # 读取商品列表
            product_wb = load_workbook(product_file)
            product_ws = product_wb.active
            
            # 获取表头
            violation_headers = [cell.value for cell in violation_ws[1]]
            product_headers = [cell.value for cell in product_ws[1]]
            
            # 检查必要的列是否存在
            if 'SPUID' not in violation_headers or '商品ID' not in product_headers:
                raise ValueError("Excel文件格式不正确，请确保包含SPUID和商品ID列")
            
            # 获取SPUID和商品ID的列索引
            spuid_col = violation_headers.index('SPUID') + 1
            product_id_col = product_headers.index('商品ID') + 1
            
            # 创建商品ID到行的映射
            product_data = {}
            for row in product_ws.iter_rows(min_row=2):
                product_id = row[product_id_col - 1].value
                if product_id:
                    product_data[product_id] = row
            
            # 创建新的工作簿
            from openpyxl import Workbook
            merged_wb = Workbook()
            merged_ws = merged_wb.active
            
            # 写入合并后的表头
            merged_headers = violation_headers + [h for h in product_headers if h != '商品ID']
            for col, header in enumerate(merged_headers, 1):
                merged_ws.cell(row=1, column=col, value=header)
            
            # 合并数据
            row_num = 2
            for row in violation_ws.iter_rows(min_row=2):
                spuid = row[spuid_col - 1].value
                
                # 写入违规列表数据
                for col, cell in enumerate(row, 1):
                    merged_ws.cell(row=row_num, column=col, value=cell.value)
                
                # 如果找到匹配的商品数据，写入商品列表数据
                if spuid in product_data:
                    product_row = product_data[spuid]
                    col_offset = len(violation_headers)
                    for col, cell in enumerate(product_row, 1):
                        if col != product_id_col:  # 跳过商品ID列
                            merged_ws.cell(row=row_num, column=col_offset + col - 1, value=cell.value)
                
                row_num += 1
            
            # 保存合并后的文件
            merged_wb.save(output_file)
            
            self.logger.info(f"数据已成功合并并保存到: {output_file}")
            messagebox.showinfo("成功", "数据合并完成！")
            
        except Exception as e:
            error_msg = f"合并Excel文件时出错: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("错误", error_msg) 