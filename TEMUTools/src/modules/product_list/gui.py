import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import logging
import csv
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
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
        
        # 设置UI
        self.setup_ui()
        
        # 配置日志处理器
        self.setup_logging()
        
        # 加载保存的参数
        self.load_last_params()
        
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
        self.logger = logging.getLogger('product_list')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        # 添加一个初始日志
        self.logger.info("商品列表管理工具已初始化")
        
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
                self.logger.info("已加载上次保存的配置")
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            # 使用默认值
            self.last_cookie = ''
            self.last_anti_content = ''
            self.last_mallid = '634418223796259'
            self.last_pages = '2'
            self.last_page_size = '20'
            self.logger.info("使用默认配置")

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
            self.logger.info("配置已保存")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {str(e)}")
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
        
        # 导出按钮框架
        export_frame = ttk.LabelFrame(button_frame, text="导出", padding="5")
        export_frame.pack(side=tk.LEFT, padx=5)
        
        # 一键导出按钮
        self.export_all_button = ttk.Button(
            export_frame,
            text="一键导出所有模板",
            command=self.export_all_templates,
            state=tk.DISABLED
        )
        self.export_all_button.pack(side=tk.LEFT, padx=2)
        
        # 分隔线
        ttk.Separator(export_frame, orient='vertical').pack(side=tk.LEFT, padx=5, fill='y')
        
        # 导出商品列表按钮
        self.export_list_button = ttk.Button(
            export_frame,
            text="导出商品列表",
            command=self.export_product_list,
            state=tk.DISABLED
        )
        self.export_list_button.pack(side=tk.LEFT, padx=2)
        
        # 导出商品码模板按钮
        self.export_code_button = ttk.Button(
            export_frame,
            text="导出商品码模板",
            command=self.export_product_code_template,
            state=tk.DISABLED
        )
        self.export_code_button.pack(side=tk.LEFT, padx=2)
        
        # 导出库存模板按钮
        self.export_inventory_button = ttk.Button(
            export_frame,
            text="导出库存模板",
            command=self.export_inventory_template,
            state=tk.DISABLED
        )
        self.export_inventory_button.pack(side=tk.LEFT, padx=2)
        
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
            self.logger.info(f"开始获取商品列表数据，计划获取 {pages} 页...")
            all_data = crawler.get_all_data(max_pages=pages)
            
            if all_data:
                self.current_data = all_data  # 保存当前数据
                self.logger.info(f"共获取到 {len(all_data)} 条数据")
                # 启用导出按钮
                self.export_list_button.configure(state='normal')
                self.export_code_button.configure(state='normal')
                self.export_inventory_button.configure(state='normal')
            else:
                self.current_data = []  # 清空当前数据
                self.logger.warning("未获取到任何数据")
                # 禁用导出按钮
                self.export_list_button.configure(state='disabled')
                self.export_code_button.configure(state='disabled')
                self.export_inventory_button.configure(state='disabled')
                
        except Exception as e:
            self.current_data = []  # 清空当前数据
            self.logger.error(f"程序执行出错: {str(e)}")
            # 禁用导出按钮
            self.export_list_button.configure(state='disabled')
            self.export_code_button.configure(state='disabled')
            self.export_inventory_button.configure(state='disabled')
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
        has_data = bool(self.current_data)
        self.export_all_button.configure(state='normal' if has_data else 'disabled')
        self.export_list_button.configure(state='normal' if has_data else 'disabled')
        self.export_code_button.configure(state='normal' if has_data else 'disabled')
        self.export_inventory_button.configure(state='normal' if has_data else 'disabled')

    def export_product_list(self):
        """导出商品列表到Excel文件"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        try:
            # 获取保存路径
            default_filename = f"商品列表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:  # 用户取消保存
                return
                
            # 准备Excel数据
            excel_data = []
            
            for product in self.current_data:
                # 基本信息
                base_info = {
                    '商品ID': product['productId'],
                    '商品名称': product['productName'],
                    '商品类型': product['productType'],
                    '来源类型': product['sourceType'],
                    '商品编码': product['goodsId'],
                    '主图URL': product['mainImageUrl'],
                    '创建时间': datetime.fromtimestamp(product['createdAt']/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    '类目ID': product['leafCat']['catId'],
                    '类目名称': product['leafCat']['catName']
                }
                
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    sku_info = base_info.copy()
                    sku_info.update({
                        'SKU ID': sku['productSkuId'],
                        'SKU编码': sku['extCode'],
                        '供应商价格': sku['supplierPrice'] / 100,  # 转换为元
                        'SKU图片': sku['thumbUrl']
                    })
                    
                    # 处理规格信息
                    for spec in sku['productSkuSpecList']:
                        sku_info[f'{spec["parentSpecName"]}'] = spec['specName']
                    
                    excel_data.append(sku_info)
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "商品列表"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 设置列顺序
            columns_order = [
                '商品ID', '商品名称', '商品类型', '来源类型', '商品编码',
                '类目ID', '类目名称', 'SKU ID', 'SKU编码', '供应商价格',
                '颜色', '尺码', '主图URL', 'SKU图片', '创建时间'
            ]
            
            # 写入表头
            for col, header in enumerate(columns_order, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入数据
            for row, data in enumerate(excel_data, 2):
                for col, header in enumerate(columns_order, 1):
                    value = data.get(header, '')
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                    cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
            logging.info(f"商品列表已导出到Excel: {file_path}")
            messagebox.showinfo("成功", "商品列表导出成功！")
            
        except Exception as e:
            error_msg = f"导出商品列表失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def export_product_code_template(self):
        """导出商品码模板"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        try:
            # 获取保存路径
            default_filename = f"商品码模板_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:  # 用户取消保存
                return
                
            # 准备Excel数据
            excel_data = []
            
            # 定义映射字典
            code_mapping = {
                "CUSHION": "CU-0608",
                "Cushion": "CU-0608",
                "SLEEVE": "BE-0608",
                "Sleeve": "BE-0608",
                "SH": "SH-0608",
                "sh": "SH-0608",
                "CB": "CB-0608",
                "cb": "CB-0608",
                "Sock": "SO-0608",
                "sock": "SO-0608",
                "drawing": "CB-0608",
                "Drawing": "CB-0608",
                "Scarf": "BE-0608",
                "scarf": "BE-0608",
                "Apron": "AP-0608",
                "apron": "AP-0608"
            }
            
            for product in self.current_data:
                product_id = product['productId']
                
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    sku_code = sku['extCode']
                    # 获取下划线前的部分
                    key = sku_code.split('_')[0] if '_' in sku_code else sku_code
                    
                    # 查找对应的商品码
                    product_code = code_mapping.get(key, "未定义")
                    
                    excel_data.append({
                        'SPUID': product_id,
                        '商品识别码': product_code
                    })
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "商品码模板"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            headers = ['SPUID', '商品识别码']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=f"{header}")
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入数据
            for row, data in enumerate(excel_data, 2):
                for col, header in enumerate(headers, 1):
                    value = data.get(header, '')
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
            logging.info(f"商品码模板已导出到Excel: {file_path}")
            messagebox.showinfo("成功", "商品码模板导出成功！")
            
        except Exception as e:
            error_msg = f"导出商品码模板失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def export_inventory_template(self):
        """导出库存模板"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        try:
            # 获取保存路径
            default_filename = f"库存模板_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:  # 用户取消保存
                return
                
            # 准备Excel数据
            excel_data = []
            
            for product in self.current_data:
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    excel_data.append({
                        'SKU ID': sku['productSkuId']
                    })
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "库存模板"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            headers = ['SKU ID', '', '', '修改后库存']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入说明行
            ws.cell(row=2, column=1, value="必填指Temu的SKU ID")
            ws.cell(row=2, column=4, value="条件必填指当前的实际总库存，导入成功后将直接覆盖线上已有库存")
            
            # 写入数据
            for row, data in enumerate(excel_data, 3):
                # SKU ID (第1列)
                cell = ws.cell(row=row, column=1, value=data['SKU ID'])
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = border
                
                # 第2、3列保持为空
                for col in [2, 3]:
                    cell = ws.cell(row=row, column=col, value="")
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    cell.border = border
                
                # 默认库存值 (第4列)
                cell = ws.cell(row=row, column=4, value=1000)
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
            logging.info(f"库存模板已导出到Excel: {file_path}")
            messagebox.showinfo("成功", "库存模板导出成功！")
            
        except Exception as e:
            error_msg = f"导出库存模板失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def export_all_templates(self):
        """一键导出所有模板"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        try:
            # 获取保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:  # 用户取消选择
                return
                
            # 生成时间戳
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 导出商品列表
            list_path = os.path.join(save_dir, f"商品列表_{timestamp}.xlsx")
            self.export_product_list_to_path(list_path)
            
            # 导出商品码模板
            code_path = os.path.join(save_dir, f"商品码模板_{timestamp}.xlsx")
            self.export_product_code_template_to_path(code_path)
            
            # 导出库存模板
            inventory_path = os.path.join(save_dir, f"库存模板_{timestamp}.xlsx")
            self.export_inventory_template_to_path(inventory_path)
            
            logging.info(f"所有模板已导出到目录: {save_dir}")
            messagebox.showinfo("成功", "所有模板导出成功！")
            
        except Exception as e:
            error_msg = f"导出模板失败: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def export_product_list_to_path(self, file_path):
        """导出商品列表到指定路径"""
        try:
            # 准备Excel数据
            excel_data = []
            
            for product in self.current_data:
                # 基本信息
                base_info = {
                    '商品ID': product['productId'],
                    '商品名称': product['productName'],
                    '商品类型': product['productType'],
                    '来源类型': product['sourceType'],
                    '商品编码': product['goodsId'],
                    '主图URL': product['mainImageUrl'],
                    '创建时间': datetime.fromtimestamp(product['createdAt']/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    '类目ID': product['leafCat']['catId'],
                    '类目名称': product['leafCat']['catName']
                }
                
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    sku_info = base_info.copy()
                    sku_info.update({
                        'SKU ID': sku['productSkuId'],
                        'SKU编码': sku['extCode'],
                        '供应商价格': sku['supplierPrice'] / 100,  # 转换为元
                        'SKU图片': sku['thumbUrl']
                    })
                    
                    # 处理规格信息
                    for spec in sku['productSkuSpecList']:
                        sku_info[f'{spec["parentSpecName"]}'] = spec['specName']
                    
                    excel_data.append(sku_info)
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "商品列表"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 设置列顺序
            columns_order = [
                '商品ID', '商品名称', '商品类型', '来源类型', '商品编码',
                '类目ID', '类目名称', 'SKU ID', 'SKU编码', '供应商价格',
                '颜色', '尺码', '主图URL', 'SKU图片', '创建时间'
            ]
            
            # 写入表头
            for col, header in enumerate(columns_order, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入数据
            for row, data in enumerate(excel_data, 2):
                for col, header in enumerate(columns_order, 1):
                    value = data.get(header, '')
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                    cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
        except Exception as e:
            raise Exception(f"导出商品列表失败: {str(e)}")

    def export_product_code_template_to_path(self, file_path):
        """导出商品码模板到指定路径"""
        try:
            # 准备Excel数据
            excel_data = []
            
            # 定义映射字典
            code_mapping = {
                "CUSHION": "CU-0608",
                "Cushion": "CU-0608",
                "SLEEVE": "BE-0608",
                "Sleeve": "BE-0608",
                "SH": "SH-0608",
                "sh": "SH-0608",
                "CB": "CB-0608",
                "cb": "CB-0608",
                "Sock": "SO-0608",
                "sock": "SO-0608",
                "drawing": "CB-0608",
                "Drawing": "CB-0608",
                "Scarf": "BE-0608",
                "scarf": "BE-0608",
                "Apron": "AP-0608",
                "apron": "AP-0608"
            }
            
            for product in self.current_data:
                product_id = product['productId']
                
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    sku_code = sku['extCode']
                    # 获取下划线前的部分
                    key = sku_code.split('_')[0] if '_' in sku_code else sku_code
                    
                    # 查找对应的商品码
                    product_code = code_mapping.get(key, "未定义")
                    
                    excel_data.append({
                        'SPUID': product_id,
                        '商品识别码': product_code
                    })
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "商品码模板"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            headers = ['SPUID', '商品识别码']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=f"{header}")
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入数据
            for row, data in enumerate(excel_data, 2):
                for col, header in enumerate(headers, 1):
                    value = data.get(header, '')
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
        except Exception as e:
            raise Exception(f"导出商品码模板失败: {str(e)}")

    def export_inventory_template_to_path(self, file_path):
        """导出库存模板到指定路径"""
        try:
            # 准备Excel数据
            excel_data = []
            
            for product in self.current_data:
                # 处理SKU信息
                for sku in product['productSkuSummaries']:
                    excel_data.append({
                        'SKU ID': sku['productSkuId']
                    })
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "库存模板"
            
            # 设置样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            headers = ['SKU ID', '', '', '修改后库存']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入说明行
            ws.cell(row=2, column=1, value="必填指Temu的SKU ID")
            ws.cell(row=2, column=4, value="条件必填指当前的实际总库存，导入成功后将直接覆盖线上已有库存")
            
            # 写入数据
            for row, data in enumerate(excel_data, 3):
                # SKU ID (第1列)
                cell = ws.cell(row=row, column=1, value=data['SKU ID'])
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = border
                
                # 第2、3列保持为空
                for col in [2, 3]:
                    cell = ws.cell(row=row, column=col, value="")
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    cell.border = border
                
                # 默认库存值 (第4列)
                cell = ws.cell(row=row, column=4, value=1000)
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = border
            
            # 保存文件
            wb.save(file_path)
            
        except Exception as e:
            raise Exception(f"导出库存模板失败: {str(e)}") 