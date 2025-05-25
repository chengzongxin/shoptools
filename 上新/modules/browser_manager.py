from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
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
        self.setup_driver()

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
            
            # 下载并设置ChromeDriver
            try:
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