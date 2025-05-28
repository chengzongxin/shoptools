import os
import requests
import zipfile
import io
import platform
from webdriver_manager.chrome import ChromeDriverManager

# 根据操作系统导入不同的模块
if platform.system() == 'Windows':
    import winreg

class ChromeDriverManager:
    """
    ChromeDriver管理器类
    负责ChromeDriver的下载、安装和版本管理
    """
    def __init__(self, debug=True):
        """
        初始化ChromeDriver管理器
        :param debug: 是否开启调试模式
        """
        self.debug = debug
        self.system = platform.system()

    def check_local_chromedriver(self):
        """
        检查本地是否已安装ChromeDriver
        :return: ChromeDriver路径或None
        """
        driver_dir = os.path.join(os.getcwd(), "drivers")
        driver_name = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
        driver_path = os.path.join(driver_dir, driver_name)
        
        if os.path.exists(driver_path):
            if self.debug:
                print(f"发现本地ChromeDriver: {driver_path}")
            return driver_path
        return None

    def get_chrome_version(self):
        """
        获取Chrome浏览器版本
        :return: Chrome版本号
        """
        try:
            # 尝试使用webdriver_manager获取版本
            return ChromeDriverManager().driver.get_version()
        except:
            if self.system == "Windows":
                # Windows系统从注册表获取
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            else:
                # Mac系统从应用程序包获取
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if os.path.exists(chrome_path):
                    import subprocess
                    result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True)
                    version = result.stdout.strip().split()[-1]
                    return version
                raise Exception("无法获取Chrome版本")

    def get_version_numbers(self, chrome_version):
        """
        生成可能的版本号列表
        :param chrome_version: 当前Chrome版本
        :return: 版本号列表
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

    def download_chromedriver(self):
        """
        手动下载ChromeDriver
        :return: ChromeDriver路径
        """
        try:
            # 首先检查本地是否已安装
            local_driver = self.check_local_chromedriver()
            if local_driver:
                return local_driver

            # 获取Chrome版本
            chrome_version = self.get_chrome_version()
            if self.debug:
                print(f"检测到Chrome版本: {chrome_version}")

            # 尝试不同的版本号
            version_numbers = self.get_version_numbers(chrome_version)
            
            for version in version_numbers:
                try:
                    if self.debug:
                        print(f"尝试ChromeDriver版本: {version}")
                    
                    # 根据操作系统选择正确的下载URL
                    if self.system == "Windows":
                        download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/chromedriver-win64.zip"
                        zip_path = "chromedriver-win64/chromedriver.exe"
                        driver_name = "chromedriver.exe"
                    else:
                        download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/mac-x64/chromedriver-mac-x64.zip"
                        zip_path = "chromedriver-mac-x64/chromedriver"
                        driver_name = "chromedriver"
                    
                    if self.debug:
                        print(f"正在下载ChromeDriver...")
                    
                    # 下载ChromeDriver
                    response = requests.get(download_url)
                    response.raise_for_status()
                    
                    # 解压文件
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        # 创建drivers目录（如果不存在）
                        driver_dir = os.path.join(os.getcwd(), "drivers")
                        os.makedirs(driver_dir, exist_ok=True)
                        
                        # 解压文件
                        zip_file.extract(zip_path, driver_dir)
                        
                        # 移动文件到正确位置
                        old_path = os.path.join(driver_dir, zip_path)
                        new_path = os.path.join(driver_dir, driver_name)
                        
                        if os.path.exists(new_path):
                            os.remove(new_path)
                        os.rename(old_path, new_path)
                        
                        # 在Mac上设置执行权限
                        if self.system != "Windows":
                            os.chmod(new_path, 0o755)
                        
                        if self.debug:
                            print(f"ChromeDriver已下载到: {new_path}")
                        
                        return new_path
                        
                except Exception as e:
                    if self.debug:
                        print(f"版本 {version} 下载失败: {str(e)}")
                    continue
            
            raise Exception("无法找到合适的ChromeDriver版本")
                
        except Exception as e:
            print(f"下载ChromeDriver失败: {str(e)}")
            raise 