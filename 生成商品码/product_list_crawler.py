import requests
import json
import time
import pandas as pd
from typing import List, Dict, Optional
import logging
from datetime import datetime
from dataclasses import dataclass
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG级别以获取更多信息
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Category:
    catId: int
    catName: str
    catEnName: Optional[str]
    catType: Optional[int]

@dataclass
class ProductProperty:
    templatePid: int
    pid: int
    refPid: int
    propName: str
    vid: int
    propValue: str
    valueUnit: str
    valueExtendInfo: str
    numberInputValue: str

@dataclass
class SkuSpec:
    parentSpecId: int
    parentSpecName: str
    specId: int
    specName: str
    unitSpecName: Optional[str]

@dataclass
class ProductSku:
    productSkuId: int
    thumbUrl: str
    productSkuSpecList: List[SkuSpec]
    extCode: str
    supplierPrice: int

@dataclass
class Product:
    productId: int
    productSkcId: int
    productName: str
    productType: int
    sourceType: int
    goodsId: int
    leafCat: Category
    categories: Dict[str, Category]
    productProperties: List[ProductProperty]
    mainImageUrl: str
    productSkuSummaries: List[ProductSku]
    createdAt: datetime

class ProductListCrawler:
    def __init__(self):
        # 基础URL
        self.base_url = "https://seller.kuajingmaihuo.com"
        self.api_url = f"{self.base_url}/bg-visage-mms/product/skc/pageQuery"
        
        # 请求头
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "0aqAfa5e-wCEsoC8XfJClMLV9eBVKXCy5dT_a6gcCFZqzqwzz3VFFs_dF2HKkiWMf1pUy1UFy8k-fzeF3LD-fFw-1R7MfRI08p-LwmM31p13ZD-fkkMCCdEu2EGfpSYNgjCNf9qO0TonqPxXTmZ_JXp_JnuTJXp4anpTYOq_YHqxb9Bao5eAuFmZezeFEdXsW-RRvzelp-fR1eL2CSkbeF3tWMFaTKRPT1B2MSByCK99pXpkbdtXann2mA4CKqdNnTUrNo_Wvn5mqy5XodnDbNT7aNuVeqXrsTsiipUr6an2AAXShqmv6y0EoHi9a2d4g3X_xqtVBKKYPCSxPJXXTVPx5gPHmCqpdMX4EUJt4UG1ocSGQg1imcKxMDQNotLyDo0I0GQnXPZo5_YXtPCfpjQlDrXxpHOY5BaX0rGQulZXtTUJGh_az-4PHs9zx0V0lTF3ke6ePkL2E_7lodblJhIlLDD813Z1OMBlsyNiLHjsaC9-k8finzuJvNj",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": "api_uid=CmaibmgXiUFPWwBPCCK/Ag==; _f77=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; _a42=55668fc2-6221-4e03-92ce-da00c700b90d; ru1k=fe503ea0-51c9-41ad-aa57-a17e3b9ed899; ru2k=55668fc2-6221-4e03-92ce-da00c700b90d; _nano_fp=XpmYl0Pbl0T8n5dalT_0tvV~PytJuNlzkGnJ1977; _bee=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; rckk=tfHT7LYhzCfWucOkWxZ5icxiBsAQXamH; SUB_PASS_ID=eyJ0IjoiYS9tY2xtZ3Byem9pUE1qWHNEYkh3UERZSGdZRERackExZ1B6WEkvenBoSU5SSlRRNnFDRzV4bXFBdlExT05WRCIsInYiOjEsInMiOjEwMDAwLCJ1IjoyNDE1MTU0NjgxNzcwMX0=; user_id=DB000-0ae91471-f434-431c-8f2e-e82bca45da22; user_session=uDebcMfnWN6dpu4T9kxfFJibCHHtmBOp0FABKe5g7PK13nAoV6e2jE3uznm2GBqsmavqzyY7oFPdytI7JFfxZtR00ZvzzVjug2jR; fingerprint=None; lingfeng_backend=backend-pro-0",
            "mallid": "634418223796259",
            "origin": "https://seller.kuajingmaihuo.com",
            "referer": "https://seller.kuajingmaihuo.com/goods/product/list",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
        }
        
        # 分页参数
        self.page_size = 20
        self.current_page = 1
        
    def get_page_data(self, page: int) -> Dict:
        """
        获取指定页码的数据
        
        Args:
            page: 页码
            
        Returns:
            Dict: 响应数据
        """
        payload = {
            "page": page,
            "pageSize": self.page_size
        }
        
        try:
            logger.info(f"正在获取第 {page} 页数据")
            logger.debug(f"请求URL: {self.api_url}")
            logger.debug(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return None
                
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            logger.error(f"响应内容: {response.text}")
            return None
        except Exception as e:
            logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return None
            
    def get_all_data(self, max_pages: int = 2) -> List[Dict]:
        """
        获取指定页数的数据
        
        Args:
            max_pages: 要获取的最大页数
            
        Returns:
            List[Dict]: 商品数据
        """
        all_data = []
        
        for page in range(1, max_pages + 1):
            result = self.get_page_data(page)
            
            if not result:
                logger.error(f"第 {page} 页数据获取失败")
                break
                
            # 获取商品列表数据
            items = result.get('result', {}).get('pageItems', [])
            if not items:
                logger.info("没有更多数据")
                break
                
            all_data.extend(items)
            logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
            
            time.sleep(1)  # 添加延迟，避免请求过快
            
        return all_data
        
    def save_to_excel(self, data: List[Dict], filename: str = None):
        """
        将数据保存为Excel文件
        
        Args:
            data: 商品数据列表
            filename: 文件名（可选）
        """
        if not data:
            logger.warning("没有数据可保存")
            return
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_list_{timestamp}.xlsx"
            
        try:
            # 准备Excel数据
            excel_data = []
            
            for product in data:
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
            
            # 创建DataFrame
            df = pd.DataFrame(excel_data)
            
            # 设置列顺序
            columns_order = [
                '商品ID', '商品名称', '商品类型', '来源类型', '商品编码',
                '类目ID', '类目名称', 'SKU ID', 'SKU编码', '供应商价格',
                '颜色', '尺码', '主图URL', 'SKU图片', '创建时间'
            ]
            
            # 只保留存在的列
            columns_order = [col for col in columns_order if col in df.columns]
            df = df[columns_order]
            
            # 保存为Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"数据已保存到文件: {filename}")
            
        except Exception as e:
            logger.error(f"保存Excel文件时发生错误: {str(e)}")
            raise  # 添加这行以显示详细错误信息

class ProductCrawlerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("商品数据爬取工具")
        self.root.geometry("800x600")
        
        # 加载上次保存的参数
        self.load_last_params()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TLabel", padding=5)
        self.style.configure("TButton", padding=5)
        self.style.configure("TEntry", padding=5)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
    def load_last_params(self):
        """加载上次保存的参数"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_cookie = config.get('cookie', '')
                    self.last_anti_content = config.get('anti_content', '')
                    self.last_mallid = config.get('mallid', '634418223796259')
                    self.last_pages = config.get('pages', '2')
                    self.last_page_size = config.get('page_size', '20')
            else:
                # 默认值
                self.last_cookie = ''
                self.last_anti_content = ''
                self.last_mallid = '634418223796259'
                self.last_pages = '2'
                self.last_page_size = '20'
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            # 使用默认值
            self.last_cookie = ''
            self.last_anti_content = ''
            self.last_mallid = '634418223796259'
            self.last_pages = '2'
            self.last_page_size = '20'

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
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logging.info("参数已保存")
        except Exception as e:
            logging.error(f"保存配置文件失败: {str(e)}")

    def create_input_fields(self):
        # 页数输入
        ttk.Label(self.main_frame, text="获取页数:").grid(row=0, column=0, sticky=tk.W)
        self.pages_var = tk.StringVar(value=self.last_pages)
        self.pages_entry = ttk.Entry(self.main_frame, textvariable=self.pages_var, width=10)
        self.pages_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 每页数据量输入
        ttk.Label(self.main_frame, text="每页数据量:").grid(row=1, column=0, sticky=tk.W)
        self.page_size_var = tk.StringVar(value=self.last_page_size)
        self.page_size_entry = ttk.Entry(self.main_frame, textvariable=self.page_size_var, width=10)
        self.page_size_entry.grid(row=1, column=1, sticky=tk.W)
        
    def create_cookie_input(self):
        # Cookie输入框架
        cookie_frame = ttk.LabelFrame(self.main_frame, text="请求头设置", padding="5")
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
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
    def create_log_area(self):
        # 创建日志文本框
        self.log_text = tk.Text(self.main_frame, height=15, width=80)
        self.log_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def create_buttons(self):
        # 创建按钮框架
        button_frame = ttk.Frame(self.main_frame)
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
        
    def setup_logging(self):
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
            
            # 保存数据
            if all_data:
                logging.info(f"共获取到 {len(all_data)} 条数据")
                crawler.save_to_excel(all_data)
                logging.info("数据保存完成")
            else:
                logging.warning("未获取到任何数据")
                
        except Exception as e:
            logging.error(f"程序执行出错: {str(e)}")
        finally:
            # 恢复界面状态
            self.root.after(0, self.reset_ui)
            
    def stop_crawling(self):
        # TODO: 实现停止功能
        self.stop_button.configure(state='disabled')
        logging.info("正在停止爬取...")
        
    def reset_ui(self):
        # 恢复界面状态
        self.pages_entry.configure(state='normal')
        self.page_size_entry.configure(state='normal')
        self.cookie_entry.configure(state='normal')
        self.anti_content_entry.configure(state='normal')
        self.mallid_entry.configure(state='normal')
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        
    def run(self):
        self.root.mainloop()

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='商品数据爬取工具')
    parser.add_argument('--pages', type=int, default=2, help='要获取的页数（默认：2）')
    parser.add_argument('--page-size', type=int, default=20, help='每页数据量（默认：20）')
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = ProductListCrawler()
    crawler.page_size = args.page_size  # 设置每页数据量
    
    try:
        # 获取数据
        logger.info(f"开始获取商品列表数据，计划获取 {args.pages} 页...")
        all_data = crawler.get_all_data(max_pages=args.pages)
        
        # 保存数据
        if all_data:
            logger.info(f"共获取到 {len(all_data)} 条数据")
            crawler.save_to_excel(all_data)
            logger.info("数据保存完成")
        else:
            logger.warning("未获取到任何数据")
            
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    app = ProductCrawlerGUI()
    app.run() 