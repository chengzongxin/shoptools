from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import socket
import subprocess
import platform
import os
import sys
from .chrome_driver_manager import ChromeDriverManager

class BrowserManager:
    """
    浏览器管理类
    负责浏览器的初始化、配置和管理
    """
    def __init__(self, debug=True):
        """
        初始化浏览器管理器
        :param debug: 是否开启调试模式
        """
        self.driver = None
        self.wait = None
        self.debug = debug
        self.chromedriver_path = self._get_chromedriver_path()
        self.system = platform.system()
        # print("开始检查浏览器状态...")
        # self.check_and_start_browser()
        # print("开始配置Chrome选项...")
        self.setup_driver()

    def _get_resource_path(self, relative_path):
        """
        获取资源的绝对路径，支持开发环境和打包后的环境
        :param relative_path: 相对路径
        :return: 绝对路径
        """
        try:
            # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

    def _get_chromedriver_path(self):
        """
        获取ChromeDriver的路径
        :return: ChromeDriver的路径
        """
        if self.debug:
            print("正在获取ChromeDriver路径...")
        
        # 获取chromedriver路径
        chromedriver_path = self._get_resource_path(os.path.join("drivers", "chromedriver.exe"))
        
        if self.debug:
            print(f"ChromeDriver路径: {chromedriver_path}")
            print(f"ChromeDriver是否存在: {os.path.exists(chromedriver_path)}")
        
        return chromedriver_path

    def check_port(self, port):
        """
        检查指定端口是否在监听
        :param port: 端口号
        :return: 是否在监听
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"检查端口失败: {str(e)}")
            return False

    def start_chrome(self):
        """
        启动Chrome浏览器
        :return: 是否启动成功
        """
        try:
            if self.system == "Windows":
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                user_data_dir = r"C:\selenum\ChromeProfile"
            else:
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                user_data_dir = os.path.expanduser("~/selenium/ChromeProfile")
            
            # 确保用户数据目录存在
            os.makedirs(user_data_dir, exist_ok=True)
            
            # 构建启动命令
            if self.system == "Windows":
                cmd = f'"{chrome_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}"'
            else:
                cmd = f'"{chrome_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}"'
            
            if self.debug:
                print("正在启动Chrome浏览器...")
            
            # 使用subprocess启动浏览器
            subprocess.Popen(cmd, shell=True)
            
            # 等待浏览器启动
            time.sleep(5)
            
            if self.debug:
                print("Chrome浏览器启动完成")
            
            return True
            
        except Exception as e:
            print(f"启动Chrome浏览器失败: {str(e)}")
            return False

    def check_and_start_browser(self):
        """
        检查并启动浏览器
        """
        try:
            if self.debug:
                print("检查浏览器状态...")
            
            # 检查9222端口是否在监听
            if not self.check_port(9222):
                if self.debug:
                    print("浏览器未启动，准备启动...")
                
                # 启动浏览器
                if not self.start_chrome():
                    raise Exception("启动浏览器失败")
                
                # 再次检查端口
                if not self.check_port(9222):
                    raise Exception("浏览器启动后端口仍未就绪")
                
                if self.debug:
                    print("浏览器启动成功")
            else:
                if self.debug:
                    print("浏览器已经在运行")
                
        except Exception as e:
            print(f"检查并启动浏览器失败: {str(e)}")
            raise

    def setup_driver(self):
        """
        设置并启动Chrome浏览器
        """
        try:
            if self.debug:
                print("开始配置Chrome选项...")
            
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            if self.debug:
                print("Chrome选项配置完成")
                print("正在检查ChromeDriver...")
            
            # 使用指定的ChromeDriver或下载新的
            try:
                if self.chromedriver_path and os.path.exists(self.chromedriver_path):
                    service = Service(self.chromedriver_path)
                else:
                    driver_manager = ChromeDriverManager(self.debug)
                    driver_path = driver_manager.download_chromedriver()
                    service = Service(driver_path)
            except Exception as e:
                print(f"ChromeDriver安装失败: {str(e)}")
                raise
            
            if self.debug:
                print("ChromeDriver准备就绪")
                print("正在连接到Chrome浏览器...")
            
            # 初始化WebDriver
            try:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                if not self.driver:
                    raise Exception("WebDriver初始化失败")
            except Exception as e:
                print(f"WebDriver初始化失败: {str(e)}")
                raise
            
            if self.debug:
                print("成功连接到Chrome浏览器")
                print("正在设置等待时间...")
            
            # 设置隐式等待时间
            self.driver.implicitly_wait(10)  # 10秒隐式等待
            
            # 设置显式等待
            self.wait = WebDriverWait(self.driver, 20)  # 20秒显式等待
            
            if self.debug:
                print("浏览器连接成功！")
                
        except Exception as e:
            print(f"浏览器连接失败：{str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise

    def open_new_tab(self, url):
        """
        打开新标签页
        :param url: 要访问的URL
        """
        try:
            # 执行JavaScript打开新标签页
            self.driver.execute_script("window.open('');")
            
            # 切换到新标签页
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 访问URL
            self.driver.get(url)
            
            if self.debug:
                print(f"成功打开新标签页并访问: {url}")
                
        except Exception as e:
            print(f"打开新标签页失败: {str(e)}")
            raise

    def click_batch_upload_button(self):
        """
        点击批量上传合规信息按钮
        """
        try:
            if self.debug:
                print("正在查找批量上传按钮...")
            
            # 等待按钮出现并点击
            button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '批量上传合规信息')]"))
            )
            
            # 点击按钮
            button.click()
            
            if self.debug:
                print("成功点击批量上传按钮")
                
        except Exception as e:
            print(f"点击批量上传按钮失败: {str(e)}")
            raise

    def close(self):
        """
        关闭浏览器
        """
        if self.driver:
            try:
                self.driver.quit()
                if self.debug:
                    print("浏览器已关闭！")
            except Exception as e:
                print(f"关闭浏览器时发生错误：{str(e)}") 