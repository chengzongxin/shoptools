import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import os
from datetime import datetime
from .crawler import ComplianceUploader
from ..system_config.config import SystemConfig

class ComplianceUploaderTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config = SystemConfig()
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.log_text = tk.Text(log_frame, height=15, width=100, state='disabled')
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        self.start_button = ttk.Button(button_frame, text="开始批量上传", command=self.start_upload)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_upload, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def setup_logging(self):
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
        self.logger = logging.getLogger('compliance_uploader')
        self.logger.setLevel(logging.INFO)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'compliance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.logger.info("合规批量上传工具已初始化")
        self.logger.info(f"日志文件保存在: {log_file}")

    def start_upload(self):
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_var.set(0)
        self.uploader = ComplianceUploader(
            logger=self.logger,
            progress_callback=self.update_progress
        )
        self._stop_flag = False
        self.upload_thread = threading.Thread(target=self.run_upload)
        self.upload_thread.start()

    def run_upload(self):
        try:
            self.uploader.batch_upload_all()
            self.after(0, lambda: messagebox.showinfo("完成", "所有合规信息已批量上传完成！"))
        except Exception as e:
            import traceback
            self.logger.error(f"批量上传失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.after(0, lambda: messagebox.showerror("错误", f"批量上传失败: {str(e)}"))
        finally:
            self.after(0, lambda: self.start_button.config(state='normal'))
            self.after(0, lambda: self.stop_button.config(state='disabled'))

    def stop_upload(self):
        # 这里只能提示用户手动终止线程
        self.logger.info("如需强制终止，请关闭程序窗口。")
        messagebox.showinfo("提示", "如需强制终止，请关闭程序窗口。")

    def update_progress(self, value):
        self.progress_var.set(value) 