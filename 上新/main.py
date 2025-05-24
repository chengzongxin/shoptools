from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import os
import requests
import zipfile
import io
from config import BROWSER_CONFIG, WAIT_CONFIG, DEBUG

class WebAutomation:
    def __init__(self):
        """
        初始化Web自动化类
        """
        self.driver = None
        self.wait = None
        self.setup_driver()

    def check_local_chromedriver(self):
        """
        检查本地是否已安装ChromeDriver
        """
        driver_dir = os.path.join(os.getcwd(), "drivers")
        driver_path = os.path.join(driver_dir, "chromedriver.exe")
        
        if os.path.exists(driver_path):
            if DEBUG:
                print(f"发现本地ChromeDriver: {driver_path}")
            return driver_path
        return None

    def download_chromedriver(self):
        """
        手动下载ChromeDriver
        """
        try:
            # 首先检查本地是否已安装
            local_driver = self.check_local_chromedriver()
            if local_driver:
                return local_driver

            # 获取Chrome版本
            chrome_version = self.get_chrome_version()
            if DEBUG:
                print(f"检测到Chrome版本: {chrome_version}")

            # 尝试不同的版本号
            version_numbers = self.get_version_numbers(chrome_version)
            
            for version in version_numbers:
                try:
                    if DEBUG:
                        print(f"尝试ChromeDriver版本: {version}")
                    
                    # 构建下载URL
                    download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/chromedriver-win64.zip"
                    
                    if DEBUG:
                        print(f"正在下载ChromeDriver...")
                    
                    # 下载ChromeDriver
                    response = requests.get(download_url)
                    response.raise_for_status()  # 检查响应状态
                    
                    # 解压文件
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        # 创建drivers目录（如果不存在）
                        driver_dir = os.path.join(os.getcwd(), "drivers")
                        os.makedirs(driver_dir, exist_ok=True)
                        
                        # 解压文件
                        zip_file.extract("chromedriver-win64/chromedriver.exe", driver_dir)
                        
                        # 移动文件到正确位置
                        old_path = os.path.join(driver_dir, "chromedriver-win64", "chromedriver.exe")
                        new_path = os.path.join(driver_dir, "chromedriver.exe")
                        
                        if os.path.exists(new_path):
                            os.remove(new_path)
                        os.rename(old_path, new_path)
                        
                        if DEBUG:
                            print(f"ChromeDriver已下载到: {new_path}")
                        
                        return new_path
                        
                except Exception as e:
                    if DEBUG:
                        print(f"版本 {version} 下载失败: {str(e)}")
                    continue
            
            raise Exception("无法找到合适的ChromeDriver版本")
                
        except Exception as e:
            print(f"下载ChromeDriver失败: {str(e)}")
            raise

    def get_version_numbers(self, chrome_version):
        """
        生成可能的版本号列表
        """
        major_version = int(chrome_version.split('.')[0])
        versions = []
        
        # 添加当前版本
        versions.append(chrome_version)
        
        # 添加主版本号
        versions.append(f"{major_version}.0.0.0")
        
        # 添加一些常见的稳定版本
        stable_versions = [
            "114.0.5735.90",
            "115.0.5790.102",
            "116.0.5845.96",
            "117.0.5938.62",
            "118.0.5993.70",
            "119.0.6045.105",
            "120.0.6099.109",
            "121.0.6167.85",
            "122.0.6261.94",
            "123.0.6312.58"
        ]
        
        versions.extend(stable_versions)
        return versions

    def get_chrome_version(self):
        """
        获取Chrome浏览器版本
        """
        try:
            # 尝试使用webdriver_manager获取版本
            return ChromeDriverManager().driver.get_version()
        except:
            # 如果失败，尝试从注册表获取
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version

    def setup_driver(self):
        """
        设置并启动Chrome浏览器
        """
        try:
            if DEBUG:
                print("开始配置Chrome选项...")
            
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            if DEBUG:
                print("Chrome选项配置完成")
                print("正在检查ChromeDriver...")
            
            # 下载并设置ChromeDriver
            try:
                driver_path = self.download_chromedriver()
                service = Service(driver_path)
            except Exception as e:
                print(f"ChromeDriver安装失败: {str(e)}")
                raise
            
            if DEBUG:
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
            
            if DEBUG:
                print("成功连接到Chrome浏览器")
                print("正在设置等待时间...")
            
            # 设置隐式等待时间
            self.driver.implicitly_wait(WAIT_CONFIG['implicit_wait'])
            
            # 设置显式等待
            self.wait = WebDriverWait(self.driver, WAIT_CONFIG['explicit_wait'])
            
            if DEBUG:
                print("浏览器连接成功！")
                
        except Exception as e:
            print(f"浏览器连接失败：{str(e)}")
            print(f"错误类型：{type(e).__name__}")
            print(f"错误详情：{sys.exc_info()}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise

    def open_new_tab(self, url):
        """
        打开新标签页
        """
        try:
            # 执行JavaScript打开新标签页
            self.driver.execute_script("window.open('');")
            
            # 切换到新标签页
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # 访问URL
            self.driver.get(url)
            
            if DEBUG:
                print(f"成功打开新标签页并访问: {url}")
                
        except Exception as e:
            print(f"打开新标签页失败: {str(e)}")
            raise

    def close(self):
        """
        关闭浏览器
        """
        if self.driver:
            try:
                self.driver.quit()
                if DEBUG:
                    print("浏览器已关闭！")
            except Exception as e:
                print(f"关闭浏览器时发生错误：{str(e)}")

def main():
    """
    主函数
    """
    automation = None
    try:
        if DEBUG:
            print("开始创建自动化实例...")
            print(f"当前工作目录: {os.getcwd()}")
            print(f"Python版本: {sys.version}")
        
        # 创建自动化实例
        automation = WebAutomation()
        
        if DEBUG:
            print("正在打开新标签页...")
        
        # 打开新标签页并访问百度
        automation.open_new_tab("https://www.baidu.com")
        time.sleep(2)  # 等待2秒
        
        if DEBUG:
            print("自动化操作完成！")
            
    except Exception as e:
        print(f"发生错误：{str(e)}")
        print(f"错误类型：{type(e).__name__}")
        print(f"错误详情：{sys.exc_info()}")
    finally:
        # 确保浏览器被正确关闭
        if automation:
            automation.close()

if __name__ == "__main__":
    main() 