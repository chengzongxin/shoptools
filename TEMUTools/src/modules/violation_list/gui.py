import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import logging
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .crawler import ViolationListCrawler
from ..system_config.config import SystemConfig

class ViolationListTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_data = []  # 存储当前获取的数据
        self.config = SystemConfig()
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        """设置用户界面"""
        # 页数输入
        ttk.Label(self, text="获取页数:").grid(row=0, column=0, sticky=tk.W)
        self.pages_var = tk.StringVar(value="1")
        self.pages_entry = ttk.Entry(self, textvariable=self.pages_var, width=10)
        self.pages_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 每页数据量输入
        ttk.Label(self, text="每页数量:").grid(row=1, column=0, sticky=tk.W)
        self.page_size_var = tk.StringVar(value="100")
        self.page_size_entry = ttk.Entry(self, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=1, column=1, sticky=tk.W)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 日志显示
        self.log_text = tk.Text(self, height=15, width=80)
        self.log_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 开始和停止按钮
        self.start_button = ttk.Button(button_frame, text="开始获取", command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_crawling, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮框架
        export_frame = ttk.LabelFrame(button_frame, text="导出", padding="5")
        export_frame.pack(side=tk.LEFT, padx=5)
        
        # 导出Excel按钮
        self.export_button = ttk.Button(
            export_frame,
            text="导出违规列表",
            command=self.export_to_excel,
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.LEFT, padx=2)
        
        # 合并Excel按钮
        self.merge_button = ttk.Button(
            export_frame,
            text="合并Excel",
            command=self.merge_excel_files
        )
        self.merge_button.pack(side=tk.LEFT, padx=2)
        
        # 清空按钮
        self.clear_button = ttk.Button(
            button_frame,
            text="清空",
            command=self.clear_all
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

    def setup_logging(self):
        """设置日志处理器"""
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
        
        self.logger = logging.getLogger('violation_list')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        self.logger.info("违规商品列表工具已初始化")

    def start_crawling(self):
        """开始爬取数据"""
        try:
            pages = int(self.pages_var.get())
            page_size = int(self.page_size_var.get())
            
            if pages <= 0 or page_size <= 0:
                messagebox.showerror("错误", "页数和每页数据量必须大于0")
                return
                
            # 禁用开始按钮，启用停止按钮
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            # 清空日志
            self.log_text.delete(1.0, tk.END)
            
            # 在新线程中运行爬虫
            self.crawler_thread = threading.Thread(
                target=self.run_crawler,
                args=(pages, page_size)
            )
            self.crawler_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def run_crawler(self, pages, page_size):
        """在新线程中运行爬虫"""
        try:
            crawler = ViolationListCrawler(logger=self.logger)
            self.logger.info(f"开始获取违规商品列表数据，计划获取 {pages} 页...")
            
            all_data = crawler.get_all_data(max_pages=pages, page_size=page_size)
            
            if all_data:
                self.current_data = all_data
                self.logger.info(f"共获取到 {len(all_data)} 条数据")
                self.export_button.configure(state='normal')
            else:
                self.current_data = []
                self.logger.warning("未获取到任何数据")
                self.export_button.configure(state='disabled')
                
        except Exception as e:
            self.current_data = []
            self.logger.error(f"程序执行出错: {str(e)}")
            self.export_button.configure(state='disabled')
        finally:
            # 在主线程中重置UI
            self.after(0, self.reset_ui)

    def stop_crawling(self):
        """停止爬取"""
        self.stop_button.configure(state='disabled')
        self.logger.info("正在停止获取...")

    def reset_ui(self):
        """重置UI状态"""
        self.pages_entry.configure(state='normal')
        self.page_size_entry.configure(state='normal')
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        
        # 根据是否有数据来启用/禁用导出按钮
        has_data = bool(self.current_data)
        self.export_button.configure(state='normal' if has_data else 'disabled')

    def clear_all(self):
        """清空所有内容"""
        self.pages_var.set("1")
        self.page_size_var.set("100")
        
        # 清空日志
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # 清空数据
        self.current_data = []
        
        # 禁用导出按钮
        self.export_button.config(state='disabled')
        
        self.logger.info("已清空所有内容")

    def export_to_excel(self):
        """导出数据到Excel"""
        if not self.current_data:
            messagebox.showinfo("提示", "没有数据可导出")
            return
        
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"违规商品列表_{timestamp}.xlsx"
            
            # 获取保存路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:  # 用户取消保存
                return
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "违规商品列表"
            
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
            headers = [
                "SPUID", "商品名称", "违规原因", "违规描述",
                "处罚类型", "处罚影响", "违规详情", "整改建议",
                "开始时间", "结束时间", "申诉状态", "申诉次数", "最大申诉次数"
            ]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
                # 设置列宽
                ws.column_dimensions[get_column_letter(col)].width = 20
            
            # 写入数据
            row = 2
            for product in self.current_data:
                # 获取第一个处罚详情（如果有的话）
                punish_detail = product.get('punish_detail_list', [{}])[0] if product.get('punish_detail_list') else {}
                
                # 获取违规详情
                illegal_details = punish_detail.get('illegal_detail', [])
                illegal_desc = '; '.join([
                    f"{illegal.get('title', '')}: {illegal.get('value', '')}"
                    for illegal in illegal_details
                ])
                
                # 格式化时间戳
                start_time = self.format_timestamp(punish_detail.get('start_time'))
                end_time = self.format_timestamp(punish_detail.get('plan_end_time'))
                
                # 写入一行数据
                ws.cell(row=row, column=1, value=product.get('spu_id', ''))
                ws.cell(row=row, column=2, value=product.get('goods_name', ''))
                ws.cell(row=row, column=3, value=product.get('leaf_reason_name', ''))
                ws.cell(row=row, column=4, value=product.get('violation_desc', ''))
                ws.cell(row=row, column=5, value=punish_detail.get('punish_appeal_type', ''))
                ws.cell(row=row, column=6, value=punish_detail.get('punish_infect_desc', ''))
                ws.cell(row=row, column=7, value=illegal_desc)
                ws.cell(row=row, column=8, value=punish_detail.get('rectification_suggestion', ''))
                ws.cell(row=row, column=9, value=start_time)
                ws.cell(row=row, column=10, value=end_time)
                ws.cell(row=row, column=11, value=self.format_appeal_status(punish_detail.get('appeal_status', 0)))
                ws.cell(row=row, column=12, value=punish_detail.get('now_appeal_time', 0))
                ws.cell(row=row, column=13, value=punish_detail.get('max_appeal_time', 0))
                
                row += 1
            
            # 调整列宽
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column].width = adjusted_width
            
            # 保存文件
            wb.save(file_path)
            
            self.logger.info(f"数据已成功导出到: {file_path}")
            messagebox.showinfo("成功", "违规商品列表导出成功！")
            
        except Exception as e:
            error_msg = f"导出Excel时出错: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def format_timestamp(self, timestamp: int) -> str:
        """格式化时间戳为可读时间"""
        if not timestamp:
            return ''
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return ''

    def format_appeal_status(self, status: int) -> str:
        """格式化申诉状态"""
        status_map = {
            0: '未申诉',
            1: '申诉中',
            2: '申诉通过',
            3: '申诉驳回'
        }
        return status_map.get(status, '未知状态')

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