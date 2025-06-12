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
from ..system_config.config import SystemConfig

class ProductListTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 初始化默认值
        self.config = SystemConfig()
        self.current_data = []  # 存储当前获取的数据
        
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
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def create_input_fields(self, parent):
        """创建输入字段"""
        # 页数输入
        ttk.Label(parent, text="获取页数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pages_var = tk.StringVar(value="2")
        self.pages_entry = ttk.Entry(parent, textvariable=self.pages_var, width=10)
        self.pages_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 每页数据量输入
        ttk.Label(parent, text="每页数据量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.page_size_var = tk.StringVar(value="20")
        self.page_size_entry = ttk.Entry(parent, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
    def create_progress_bar(self, parent):
        """创建进度条"""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            parent,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 开始爬取按钮
        self.start_button = ttk.Button(
            button_frame,
            text="开始爬取",
            command=self.start_crawling
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_crawling,
            state='disabled'
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # 导出数据按钮
        self.export_button = ttk.Button(
            button_frame,
            text="导出数据",
            command=self.export_product_list,
            state='disabled'
        )
        self.export_button.grid(row=0, column=2, padx=5)
        
        # 导出模板按钮
        self.export_template_button = ttk.Button(
            button_frame,
            text="导出模板",
            command=self.export_all_templates,
            state='disabled'
        )
        self.export_template_button.grid(row=0, column=3, padx=5)
        
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
        
    def start_crawling(self):
        """开始爬取数据"""
        try:
            pages = int(self.pages_var.get())
            page_size = int(self.page_size_var.get())
            
            if pages <= 0 or page_size <= 0:
                messagebox.showerror("错误", "页数和每页数据量必须大于0")
                return
                
            # 获取系统配置
            cookie = self.config.get_seller_cookie()
            mallid = self.config.get_mallid()
            
            if not cookie or not mallid:
                messagebox.showerror("错误", "请先在系统配置中设置Cookie和MallID")
                return
                
            # 禁用开始按钮,启用停止按钮
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # 清空进度条
            self.progress_var.set(0)
            
            # 创建爬虫实例
            self.crawler = ProductListCrawler(
                cookie=cookie,
                mallid=mallid,
                logger=self.logger,
                progress_callback=self.update_progress
            )
            
            # 在新线程中运行爬虫
            self.crawler_thread = threading.Thread(
                target=self.run_crawler,
                args=(pages, page_size, cookie, mallid)
            )
            self.crawler_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            self.logger.error(f"启动爬虫失败: {str(e)}")
            messagebox.showerror("错误", f"启动爬虫失败: {str(e)}")
            
    def run_crawler(self, pages, page_size, cookie, mallid):
        """运行爬虫"""
        try:
            self.current_data = self.crawler.crawl(pages, page_size)
            
            # 启用导出按钮
            self.export_button.config(state='normal')
            self.export_template_button.config(state='normal')
            
            self.logger.info(f"成功获取 {len(self.current_data)} 条数据")
            messagebox.showinfo("成功", f"成功获取 {len(self.current_data)} 条数据")
            
        except Exception as e:
            self.logger.error(f"爬取数据失败: {str(e)}")
            messagebox.showerror("错误", f"爬取数据失败: {str(e)}")
        finally:
            # 恢复按钮状态
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
    def stop_crawling(self):
        """停止爬取"""
        if hasattr(self, 'crawler'):
            self.crawler.stop()
            self.logger.info("已停止爬取")
            
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        
    def export_product_list(self):
        """导出商品列表"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有数据可导出")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="导出商品列表"
            )
            
            if file_path:
                self.export_product_list_to_path(file_path)
                self.logger.info(f"商品列表已导出到: {file_path}")
                messagebox.showinfo("成功", "商品列表导出成功")
                
        except Exception as e:
            self.logger.error(f"导出商品列表失败: {str(e)}")
            messagebox.showerror("错误", f"导出商品列表失败: {str(e)}")
            
    def export_all_templates(self):
        """导出所有模板"""
        if not self.current_data:
            messagebox.showwarning("警告", "没有数据可导出")
            return
            
        try:
            # 选择保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if not save_dir:
                return
                
            # 导出商品码模板
            code_template_path = os.path.join(save_dir, "商品码模板.xlsx")
            self.export_product_code_template_to_path(code_template_path)
            
            # 导出库存模板
            inventory_template_path = os.path.join(save_dir, "库存模板.xlsx")
            self.export_inventory_template_to_path(inventory_template_path)
            
            self.logger.info(f"所有模板已导出到: {save_dir}")
            messagebox.showinfo("成功", "所有模板导出成功")
            
        except Exception as e:
            self.logger.error(f"导出模板失败: {str(e)}")
            messagebox.showerror("错误", f"导出模板失败: {str(e)}")
            
    def export_product_list_to_path(self, file_path):
        """导出商品列表到指定路径"""
        wb = Workbook()
        ws = wb.active
        ws.title = "商品列表"
        
        # 设置表头
        headers = ["商品ID", "商品名称", "商品编码", "价格", "库存", "状态"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
            
        # 写入数据
        for row, item in enumerate(self.current_data, 2):
            ws.cell(row=row, column=1).value = item.get("id", "")
            ws.cell(row=row, column=2).value = item.get("name", "")
            ws.cell(row=row, column=3).value = item.get("code", "")
            ws.cell(row=row, column=4).value = item.get("price", "")
            ws.cell(row=row, column=5).value = item.get("stock", "")
            ws.cell(row=row, column=6).value = item.get("status", "")
            
        # 调整列宽
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15
            
        # 保存文件
        wb.save(file_path)
        
    def export_product_code_template_to_path(self, file_path):
        """导出商品码模板到指定路径"""
        wb = Workbook()
        ws = wb.active
        ws.title = "商品码模板"
        
        # 设置表头
        headers = ["商品ID", "商品名称", "商品编码"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
            
        # 写入数据
        for row, item in enumerate(self.current_data, 2):
            ws.cell(row=row, column=1).value = item.get("id", "")
            ws.cell(row=row, column=2).value = item.get("name", "")
            ws.cell(row=row, column=3).value = item.get("code", "")
            
        # 调整列宽
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15
            
        # 保存文件
        wb.save(file_path)
        
    def export_inventory_template_to_path(self, file_path):
        """导出库存模板到指定路径"""
        wb = Workbook()
        ws = wb.active
        ws.title = "库存模板"
        
        # 设置表头
        headers = ["商品ID", "商品名称", "商品编码", "库存数量"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
            
        # 写入数据
        for row, item in enumerate(self.current_data, 2):
            ws.cell(row=row, column=1).value = item.get("id", "")
            ws.cell(row=row, column=2).value = item.get("name", "")
            ws.cell(row=row, column=3).value = item.get("code", "")
            ws.cell(row=row, column=4).value = item.get("stock", "")
            
        # 调整列宽
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15
            
        # 保存文件
        wb.save(file_path) 