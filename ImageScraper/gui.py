import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from scraper import download_sticker_image, extract_product_name
import requests
from tqdm import tqdm
import threading

class ImageScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器")
        self.root.geometry("600x400")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入文件夹选择
        ttk.Label(self.main_frame, text="链接文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="浏览", command=self.select_input_folder).grid(row=0, column=2)
        
        # 输出文件夹选择
        ttk.Label(self.main_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.main_frame, text="浏览", command=self.select_output_folder).grid(row=1, column=2)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=2, column=0, columnspan=3, pady=20)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=3)
        
        # 开始按钮
        self.start_button = ttk.Button(self.main_frame, text="开始下载", command=self.start_download)
        self.start_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 日志文本框
        self.log_text = tk.Text(self.main_frame, height=10, width=60)
        self.log_text.grid(row=5, column=0, columnspan=3, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="选择链接文件夹")
        if folder:
            self.input_path.set(folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_path.set(folder)
            
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def start_download(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()
        
        if not input_folder or not output_folder:
            messagebox.showerror("错误", "请选择输入和输出文件夹")
            return
            
        # 禁用开始按钮
        self.start_button.configure(state='disabled')
        
        # 在新线程中运行下载任务
        thread = threading.Thread(target=self.download_task, args=(input_folder, output_folder))
        thread.daemon = True
        thread.start()
        
    def download_task(self, input_folder, output_folder):
        try:
            # 获取所有txt文件
            txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
            if not txt_files:
                self.log("未找到txt文件")
                return
                
            total_files = len(txt_files)
            for i, txt_file in enumerate(txt_files):
                # 更新状态
                self.status_var.set(f"处理文件 {i+1}/{total_files}: {txt_file}")
                self.log(f"\n处理文件: {txt_file}")
                
                # 创建输出子文件夹
                base_name = os.path.splitext(txt_file)[0]
                output_subfolder = os.path.join(output_folder, base_name)
                os.makedirs(output_subfolder, exist_ok=True)
                
                # 读取链接
                with open(os.path.join(input_folder, txt_file), 'r', encoding='utf-8') as f:
                    links = [line.strip() for line in f if line.strip()]
                
                # 下载图片
                session = requests.Session()
                success_count = 0
                for j, url in enumerate(links):
                    if download_sticker_image(url, session, output_subfolder):
                        success_count += 1
                    # 更新进度
                    progress = (i * 100 + (j + 1) * 100 / len(links)) / total_files
                    self.update_progress(progress)
                    
                self.log(f"文件 {txt_file} 下载完成，成功下载 {success_count} 张图片")
                
            self.status_var.set("下载完成")
            messagebox.showinfo("完成", "所有文件下载完成！")
            
        except Exception as e:
            self.log(f"发生错误: {str(e)}")
            messagebox.showerror("错误", f"下载过程中发生错误：{str(e)}")
            
        finally:
            # 重新启用开始按钮
            self.start_button.configure(state='normal')
            self.update_progress(0)

def main():
    root = tk.Tk()
    app = ImageScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 