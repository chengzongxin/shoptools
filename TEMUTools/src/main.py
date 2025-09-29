import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from collections import defaultdict
from modules.product_list.gui import ProductListTab
from modules.link_checker.gui import LinkCheckerTab
from modules.violation_list.gui import ViolationListTab
from modules.system_config.gui import SystemConfigTab
from modules.logger.gui import LogFrame
from modules.logger.logger import Logger
from modules.price_review.gui import PriceReviewTab
from modules.jit_open.gui import JitOpenTab
from modules.confirm_upload.gui import ConfirmUploadTab
from modules.compliance_uploader.gui import ComplianceUploaderTab
from modules.jit_sign.gui import JitSignTab
from modules.real_picture_uploader.gui import RealPictureUploaderTab
from modules.stock_setter.gui import StockSetterTab
from modules.jit_sign_bak.gui import JitSignTab as JitSignTabBak
from modules.bid_management.gui import BidManagementTab
from modules.system_config.websocket_cookie import start_websocket_server

class LinkCheckerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 存储当前检测到的重复链接
        self.duplicate_links = {}
        self.current_folder = ""
        
        # 创建主框架
        self.main_frame = ttk.Frame(self, padding="10")
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
        
        # 创建清空按钮
        self.clear_button = ttk.Button(
            self.main_frame,
            text="清空",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=3, pady=5, padx=5)
        
        # 创建结果显示区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding="5")
        self.result_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 创建文本框和滚动条
        self.text_area = tk.Text(self.result_frame, height=20, width=80)
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
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
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.duplicate_links.clear()
        
        # 用于存储链接和它们出现的文件
        link_dict = defaultdict(list)
        file_links = defaultdict(lambda: defaultdict(int))
        
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            if should_skip_file(filename):  # 添加文件检查
                continue
            
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
                except UnicodeDecodeError:
                    # 如果是二进制文件或编码不支持，直接跳过
                    continue
                except Exception as e:
                    self.text_area.insert(tk.END, f"无法读取文件 {filename}: {str(e)}\n")
        
        # 显示重复的链接
        found_duplicates = False
        
        # 首先检查跨文件的重复链接
        for url, files in link_dict.items():
            if len(set(files)) > 1:  # 确保链接出现在不同文件中
                found_duplicates = True
                # 按文件名排序，使用排序后的第一个文件作为主文件
                unique_files = sorted(set(files))
                
                self.duplicate_links[url] = {
                    'type': 'cross_file',
                    'files': unique_files  # 使用排序后的文件列表
                }
                self.text_area.insert(tk.END, f"\n跨文件重复链接: {url}\n")
                self.text_area.insert(tk.END, f"将保留在文件 {unique_files[0]} 中的链接\n")
                self.text_area.insert(tk.END, f"将从以下文件中删除:\n")
                for file in unique_files[1:]:
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

        # 记录处理失败的文件
        failed_files = []

        try:
            # 处理所有重复链接
            for url, info in self.duplicate_links.items():
                if info['type'] == 'cross_file':
                    # 处理跨文件的重复链接
                    for i, file in enumerate(info['files']):
                        file_path = os.path.join(self.current_folder, file)
                        try:
                            # 在 Mac 系统上修改文件权限
                            if os.name == 'posix':  # Mac/Linux 系统
                                try:
                                    os.chmod(file_path, 0o666)  # 给予读写权限
                                except Exception as e:
                                    failed_files.append(f"{file} (无法修改权限: {str(e)})")
                                    continue

                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if i == 0:  # 第一个文件保留所有链接
                                continue
                            
                            # 删除重复的链接
                            new_content = content.replace(url, '')
                            
                            # 写回文件
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                        except Exception as e:
                            failed_files.append(f"{file} ({str(e)})")
                else:  # single_file
                    # 处理单个文件中的重复链接
                    file = info['files'][0]
                    file_path = os.path.join(self.current_folder, file)
                    try:
                        # 在 Mac 系统上修改文件权限
                        if os.name == 'posix':  # Mac/Linux 系统
                            try:
                                os.chmod(file_path, 0o666)  # 给予读写权限
                            except Exception as e:
                                failed_files.append(f"{file} (无法修改权限: {str(e)})")
                                continue

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
                    except Exception as e:
                        failed_files.append(f"{file} ({str(e)})")

            # 显示处理结果
            if failed_files:
                error_message = "以下文件处理失败：\n" + "\n".join(failed_files)
                messagebox.showwarning("警告", error_message)
            else:
                messagebox.showinfo("成功", "重复链接已删除！")
            
            # 重新检查文件夹
            self.check_duplicate_links(self.current_folder)
            
        except Exception as e:
            messagebox.showerror("错误", f"删除过程中出现错误：{str(e)}")

    def clear_all(self):
        """清空所有内容"""
        # 清空当前文件夹
        self.current_folder = ""
        self.folder_label.config(text="未选择文件夹")
        
        # 清空文本框
        self.text_area.config(state='normal')  # 临时启用文本框以清空内容
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state='disabled')  # 恢复只读状态
        
        # 清空重复链接数据
        self.duplicate_links.clear()
        
        # 禁用删除按钮
        self.delete_button.config(state='disabled')

def should_skip_file(filename):
    """检查是否应该跳过某些文件"""
    skip_files = {
        '.DS_Store',  # Mac系统文件
        'Thumbs.db',  # Windows缩略图文件
        '.git',       # Git相关文件
        '__pycache__' # Python缓存文件
    }
    return any(skip in filename for skip in skip_files)

class TEMUToolsApp:
    """TEMU工具集主程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TEMU工具集 V1.4.3")
        self.logger = Logger()
        
        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # 添加合规批量上传Tab
        self.compliance_tab = ComplianceUploaderTab(self.notebook)
        self.notebook.add(self.compliance_tab, text="合规批量上传")

        # 添加商品列表Tab- 商品列表、商品码、库存
        self.product_list_tab = ProductListTab(self.notebook)
        self.notebook.add(self.product_list_tab, text="商品码、库存")

        # 添加实拍图上传Tab
        self.real_picture_tab = RealPictureUploaderTab(self.notebook)
        self.notebook.add(self.real_picture_tab, text="上传实拍图")
        
        # 开通JIT
        self.jit_open_tab = JitOpenTab(self.notebook)
        self.notebook.add(self.jit_open_tab, text="JIT开通")

        # 签署JIT
        self.jit_sign_tab = JitSignTab(self.notebook)
        self.notebook.add(self.jit_sign_tab, text="JIT签署")

        # 添加批量设置库存Tab
        self.stock_setter_tab = StockSetterTab(self.notebook)
        self.notebook.add(self.stock_setter_tab, text="批量设置库存")

        self.price_review_tab = PriceReviewTab(self.notebook)
        self.notebook.add(self.price_review_tab, text="核价管理")

        self.confirm_upload_tab = ConfirmUploadTab(self.notebook)
        self.notebook.add(self.confirm_upload_tab, text="确认上新")

        # 添加竞价管理Tab
        self.bid_management_tab = BidManagementTab(self.notebook)
        self.notebook.add(self.bid_management_tab, text="竞价管理")
        
        self.link_checker_tab = LinkCheckerTab(self.notebook)
        self.notebook.add(self.link_checker_tab, text="链接检查")

        self.violation_list_tab = ViolationListTab(self.notebook)
        self.notebook.add(self.violation_list_tab, text="违规列表")

        # 签署JIT(废弃)
        # self.jit_sign_tab_bak = JitSignTabBak(self.notebook)
        # self.notebook.add(self.jit_sign_tab_bak, text="JIT签署(废弃)")
        
        self.system_config_tab = SystemConfigTab(self.notebook)
        self.notebook.add(self.system_config_tab, text="系统配置")
        
        # 添加日志框架
        self.log_frame = LogFrame(root)
        self.log_frame.pack(fill='x', padx=5, pady=5)
        
        # 设置窗口大小和位置
        self.setup_window()
        
        # 在后台线程中启动WebSocket服务器，不阻塞主线程
        import threading
        threading.Thread(target=self._start_websocket_server_background, daemon=True).start()
        
        # 记录启动日志
        self.logger.info("TEMU工具集已启动")
    
    def _start_websocket_server_background(self):
        """在后台线程中启动WebSocket服务器"""
        import time
        # 稍微延迟一下，确保GUI完全初始化
        time.sleep(0.5)
        try:
            start_websocket_server()
            # 注意：这里不能直接调用self.logger，因为这是在后台线程中
            print("✅ WebSocket服务器启动请求已发送 (ws://localhost:8765)")
        except Exception as e:
            print(f"❌ WebSocket服务器启动失败: {e}")

    def setup_window(self):
        """设置窗口大小和位置"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小
        window_width = 1200
        window_height = 800
        
        # 计算窗口位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)

def main():
    root = tk.Tk()
    app = TEMUToolsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 