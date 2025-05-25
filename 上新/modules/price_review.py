from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .price_mapper import PriceMapper

class PriceReview:
    def __init__(self, driver, wait, debug=True):
        """
        初始化价格审核类
        :param driver: WebDriver实例
        :param wait: WebDriverWait实例
        :param debug: 是否开启调试模式
        """
        self.driver = driver
        self.wait = wait
        self.debug = debug
        self.price_mapper = PriceMapper(debug)

    def open_price_review_page(self):
        """
        打开价格审核页面
        """
        try:
            if self.debug:
                print("正在打开上新主页面...")

            # 打开上新主页面
            self.driver.get("https://seller.kuajingmaihuo.com/main/product/seller-select")
            
            # 等待页面加载
            time.sleep(3)
            
            if self.debug:
                print("页面加载完成")

        except Exception as e:
            print(f"打开价格审核页面失败: {str(e)}")
            raise

    def click_price_pending_button(self):
        """
        点击价格待确认按钮
        """
        try:
            if self.debug:
                print("正在查找价格待确认按钮...")

            # 使用CSS选择器定位按钮
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#root > div > div > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(6)'))
            )
            
            # 获取按钮文本（包含商品数量）
            button_text = button.text
            if self.debug:
                print(f"找到价格待确认按钮: {button_text}")

            # 点击按钮
            button.click()
            
            if self.debug:
                print("成功点击价格待确认按钮")

        except Exception as e:
            print(f"点击价格待确认按钮失败: {str(e)}")
            raise

    def get_product_list(self):
        """
        获取商品列表
        :return: 商品列表元素
        """
        try:
            if self.debug:
                print("正在获取商品列表...")

            # 等待商品列表加载
            product_list = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div > div > div.TB_outerWrapper_5-117-0.TB_bordered_5-117-0.TB_notTreeStriped_5-117-0 > div.TB_inner_5-117-0 > div > div.TB_body_5-117-0 > div > div > table > tbody'))
            )
            
            if self.debug:
                print("商品列表加载完成")
            
            return product_list

        except Exception as e:
            print(f"获取商品列表失败: {str(e)}")
            raise

    def get_product_info(self, row_element):
        """
        获取单个商品的信息
        :param row_element: 商品行元素
        :return: 商品信息字典
        """
        try:
            # 获取SPU信息
            spu_element = row_element.find_element(By.CSS_SELECTOR, 'div.product-info_name__pXkCK')
            spu_info = spu_element.text if spu_element else "未找到SPU信息"

            # 获取货号
            sku_element = row_element.find_element(By.CSS_SELECTOR, 'div.use-columns_infoItem__iPDoh.use-columns_light__sKFcQ')
            sku_number = sku_element.text if sku_element else "未找到货号"

            # 获取价格确认按钮
            price_button = row_element.find_element(By.CSS_SELECTOR, 'button.BTN_outerWrapper_5-111-0')
            
            # 获取价格信息
            code, min_price = self.price_mapper.get_price_info(sku_number)
            
            if self.debug:
                print(f"\n商品信息:")
                print(f"SPU: {spu_info}")
                print(f"货号: {sku_number}")
                print(f"识别码: {code}")
                print(f"最低核价: {min_price}")
                print(f"找到价格确认按钮: {price_button.text}")

            return {
                'spu': spu_info,
                'sku': sku_number,
                'code': code,
                'min_price': min_price,
                'price_button': price_button
            }

        except Exception as e:
            print(f"获取商品信息失败: {str(e)}")
            raise

    def process_product_list(self):
        """
        处理商品列表
        """
        try:
            # 获取商品列表
            product_list = self.get_product_list()
            
            # 获取所有商品行
            rows = product_list.find_elements(By.TAG_NAME, "tr")
            
            if self.debug:
                print(f"\n找到 {len(rows)} 个商品")

            # 处理每一行商品
            for index, row in enumerate(rows, 1):
                if self.debug:
                    print(f"\n处理第 {index} 个商品:")
                
                # 获取商品信息
                product_info = self.get_product_info(row)
                
                # 点击价格确认按钮
                product_info['price_button'].click()
                
                if self.debug:
                    print(f"已点击第 {index} 个商品的价格确认按钮")
                
                # 等待一下，避免操作太快
                time.sleep(1)

        except Exception as e:
            print(f"处理商品列表失败: {str(e)}")
            raise

    def start_review(self):
        """
        开始价格审核流程
        """
        try:
            # 打开价格审核页面
            self.open_price_review_page()
            
            # 点击价格待确认按钮
            self.click_price_pending_button()
            
            # 等待页面加载
            time.sleep(3)
            
            # 处理商品列表
            self.process_product_list()
            
            if self.debug:
                print("价格审核流程初始化完成")

        except Exception as e:
            print(f"价格审核流程初始化失败: {str(e)}")
            raise 