import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from collections import defaultdict

class LinkCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("链接重复检测工具")
        self.root.geometry("800x600")
        
        # 存储当前检测到的重复链接
        self.duplicate_links = {}
        self.current_folder = ""
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建选择文件夹按钮
        self.select_button = ttk.Button(
            self.main_frame, 
            text="选择文件夹", 
            command=self.select_folder
        )
        self.select_button.grid(row=0, column=0, pady=5)
        
        # 显示选中文件夹路径的标签
        self.folder_label = ttk.Label(self.main_frame, text="未选择文件夹")
        self.folder_label.grid(row=0, column=1, pady=5)
        
        # 创建删除按钮
        self.delete_button = ttk.Button(
            self.main_frame,
            text="删除重复链接",
            command=self.delete_duplicates,
            state='disabled'  # 初始状态为禁用
        )
        self.delete_button.grid(row=0, column=2, pady=5, padx=5)
        
        # 创建结果显示区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding="5")
        self.result_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 创建文本框和滚动条
        self.text_area = tk.Text(self.result_frame, height=20, width=80)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)

    def select_folder(self):
        """选择要检查的文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.folder_label.config(text=folder_path)
            self.check_duplicate_links(folder_path)

    def check_duplicate_links(self, folder_path):
        """检查文件夹中的重复链接"""
        # 清空文本框和存储的重复链接
        self.text_area.delete(1.0, tk.END)
        self.duplicate_links.clear()
        
        # 用于存储链接和它们出现的文件
        link_dict = defaultdict(list)
        file_links = defaultdict(lambda: defaultdict(int))  # 存储每个文件中的链接出现次数
        
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 使用正则表达式查找URL
                        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
                        for url in urls:
                            link_dict[url].append(filename)
                            file_links[filename][url] += 1
                except Exception as e:
                    self.text_area.insert(tk.END, f"无法读取文件 {filename}: {str(e)}\n")
        
        # 显示重复的链接
        found_duplicates = False
        
        # 首先检查跨文件的重复链接
        for url, files in link_dict.items():
            if len(set(files)) > 1:  # 确保链接出现在不同文件中
                found_duplicates = True
                self.duplicate_links[url] = {
                    'type': 'cross_file',
                    'files': list(set(files))
                }
                self.text_area.insert(tk.END, f"\n跨文件重复链接: {url}\n")
                self.text_area.insert(tk.END, f"出现在以下文件中:\n")
                for file in self.duplicate_links[url]['files']:
                    self.text_area.insert(tk.END, f"- {file}\n")
        
        # 然后检查单个文件中的重复链接
        for filename, links in file_links.items():
            for url, count in links.items():
                if count > 1:
                    found_duplicates = True
                    self.duplicate_links[url] = {
                        'type': 'single_file',
                        'files': [filename],
                        'count': count
                    }
                    self.text_area.insert(tk.END, f"\n文件 {filename} 中的重复链接: {url}\n")
                    self.text_area.insert(tk.END, f"出现次数: {count}\n")
        
        if not found_duplicates:
            self.text_area.insert(tk.END, "未发现重复链接！\n")
            self.delete_button.config(state='disabled')
        else:
            self.delete_button.config(state='normal')
        
        # 设置文本框为只读
        self.text_area.config(state='disabled')

    def delete_duplicates(self):
        """删除重复的链接"""
        if not self.duplicate_links:
            messagebox.showinfo("提示", "没有发现重复链接！")
            return

        # 确认是否删除
        if not messagebox.askyesno("确认", "确定要删除重复的链接吗？\n这将保留每个链接的第一次出现，删除后续重复项。"):
            return

        try:
            # 处理所有重复链接
            for url, info in self.duplicate_links.items():
                if info['type'] == 'cross_file':
                    # 处理跨文件的重复链接
                    for i, file in enumerate(info['files']):
                        file_path = os.path.join(self.current_folder, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if i == 0:  # 第一个文件保留所有链接
                            continue
                        
                        # 删除重复的链接
                        new_content = content.replace(url, '')
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                else:  # single_file
                    # 处理单个文件中的重复链接
                    file = info['files'][0]
                    file_path = os.path.join(self.current_folder, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 保留第一个链接，删除其他重复的链接
                    first_occurrence = content.find(url)
                    if first_occurrence != -1:
                        # 删除第一个链接之后的所有相同链接
                        new_content = content[:first_occurrence + len(url)]
                        new_content += content[first_occurrence + len(url):].replace(url, '')
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

            messagebox.showinfo("成功", "重复链接已删除！")
            # 重新检查文件夹
            self.check_duplicate_links(self.current_folder)
            
        except Exception as e:
            messagebox.showerror("错误", f"删除过程中出现错误：{str(e)}")

def main():
    root = tk.Tk()
    app = LinkCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 