from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from datetime import datetime
import os
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
        
        # 创建日志目录
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 创建日志文件（使用日期作为文件名）
        self.log_file = os.path.join(self.log_dir, f"price_review_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 如果文件不存在，添加表头
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"价格审核日志 - {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write("=" * 80 + "\n\n")

    def log_record(self, sku, spu, min_price, new_price, action):
        """
        记录价格审核日志
        :param sku: 货号
        :param spu: SPU信息
        :param min_price: 最低核价
        :param new_price: 新申报价格
        :param action: 执行的操作
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] 货号: {sku}, SPU: {spu}, 最低核价: {min_price}, 新申报价格: {new_price}, 操作: {action}\n"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
            if self.debug:
                print(f"已记录日志: {log_entry.strip()}")
                
        except Exception as e:
            print(f"记录日志失败: {str(e)}")

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

    def get_current_row(self, index):
        """
        获取当前行的元素
        :param index: 行索引（从1开始）
        :return: 当前行元素
        """
        try:
            # 等待商品列表加载
            product_list = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div > div > div.TB_outerWrapper_5-117-0.TB_bordered_5-117-0.TB_notTreeStriped_5-117-0 > div.TB_inner_5-117-0 > div > div.TB_body_5-117-0 > div > div > table > tbody'))
            )
            
            # 获取所有行
            rows = product_list.find_elements(By.TAG_NAME, "tr")
            
            if index <= len(rows):
                return rows[index - 1]
            else:
                if self.debug:
                    print(f"行索引 {index} 超出范围，总行数: {len(rows)}")
                return None
                
        except Exception as e:
            print(f"获取当前行元素失败: {str(e)}")
            return None

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

    def handle_price_confirmation(self, min_price, sku, spu):
        """
        处理价格确认弹窗
        :param min_price: 最低核价
        :param sku: 货号
        :param spu: SPU信息
        :return: 是否成功处理
        """
        try:
            if self.debug:
                print("\n开始处理价格确认弹窗...")

            # 等待弹窗出现
            modal = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/div/div/div[1]"))
            )
            
            # 获取新申报价格
            new_price_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/div/div/div[1]/div[2]/form/div/div/div/table/tbody/tr/td[5]/div/div/div/div/span/span[2]"))
            )
            new_price = float(new_price_element.text)
            
            if self.debug:
                print(f"最低核价: {min_price}")
                print(f"新申报价格: {new_price}")

            # 比较价格
            if new_price > min_price:
                if self.debug:
                    print("新申报价格大于最低核价，直接确认")

                
                # 等待用户观察
                if self.debug:
                    print("等待5秒，请观察确认结果...")
                time.sleep(5)
                
                # 点击确认提交按钮
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div/div/div[1]/div[3]/div[2]/button[1]"))
                )
                confirm_button.click()
                
                # 记录日志
                self.log_record(sku, spu, min_price, new_price, "确认提交")
                
                
            else:
                if self.debug:
                    print("新申报价格小于等于最低核价，选择放弃调整报价")
                
                # 点击下拉框
                dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='operatorType']/div/div/div/div/div/div/div/div/div/div"))
                )
                dropdown.click()
                
                # 选择"放弃调整报价"选项
                abandon_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/div/div/div/ul/li[3]"))
                )
                abandon_option.click()

                # 等待用户观察
                if self.debug:
                    print("等待5秒，请观察确认结果...")
                time.sleep(5)
                
                # 点击确认提交按钮
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div/div/div[1]/div[3]/div[2]/button[1]"))
                )
                confirm_button.click()
                
                # 记录日志
                self.log_record(sku, spu, min_price, new_price, "放弃调整报价")
                

            # 等待弹窗消失
            time.sleep(2)
            
            if self.debug:
                print("价格确认处理完成")
            
            return True

        except Exception as e:
            print(f"处理价格确认弹窗失败: {str(e)}")
            # 记录错误日志
            self.log_record(sku, spu, min_price, "获取失败", f"处理失败: {str(e)}")
            return False

    def scroll_to_element(self, element):
        """
        滚动到元素位置
        :param element: 目标元素
        """
        try:
            # 使用JavaScript滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            # 等待一下，确保滚动完成
            time.sleep(1)
            
            if self.debug:
                print("已滚动到元素位置")
                
        except Exception as e:
            print(f"滚动到元素位置失败: {str(e)}")

    def get_total_rows(self):
        """
        获取商品总数
        :return: 商品总数
        """
        try:
            # 等待商品列表加载
            product_list = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div > div > div.TB_outerWrapper_5-117-0.TB_bordered_5-117-0.TB_notTreeStriped_5-117-0 > div.TB_inner_5-117-0 > div > div.TB_body_5-117-0 > div > div > table > tbody'))
            )
            
            # 获取所有行
            rows = product_list.find_elements(By.TAG_NAME, "tr")
            
            if self.debug:
                print(f"商品总数: {len(rows)}")
            
            return len(rows)
            
        except Exception as e:
            print(f"获取商品总数失败: {str(e)}")
            return 0

    def process_product_list(self):
        """
        处理商品列表
        """
        try:
            # 获取商品总数
            total_rows = self.get_total_rows()
            
            if self.debug:
                print(f"\n找到 {total_rows} 个商品")

            # 处理每一行商品
            for index in range(1, total_rows + 1):
                try:
                    if self.debug:
                        print(f"\n处理第 {index} 个商品:")
                    
                    # 获取当前行元素
                    row = self.get_current_row(index)
                    if row is None:
                        print(f"无法获取第 {index} 个商品，跳过")
                        continue
                    
                    # 滚动到当前商品位置
                    self.scroll_to_element(row)
                    
                    # 重新获取商品信息
                    product_info = self.get_product_info(row)
                    
                    # 点击价格确认按钮
                    product_info['price_button'].click()
                    
                    # 处理价格确认弹窗
                    if product_info['min_price'] is not None:
                        self.handle_price_confirmation(
                            product_info['min_price'],
                            product_info['sku'],
                            product_info['spu']
                        )
                    
                    if self.debug:
                        print(f"已处理第 {index} 个商品")
                    
                    # 等待一下，避免操作太快
                    time.sleep(2)
                    
                except StaleElementReferenceException:
                    if self.debug:
                        print(f"处理第 {index} 个商品时元素已过期，重试...")
                    # 重试当前商品
                    index -= 1
                    continue
                except Exception as e:
                    print(f"处理第 {index} 个商品时发生错误: {str(e)}")
                    # 记录错误日志
                    self.log_record(
                        f"第{index}个商品",
                        "获取失败",
                        "获取失败",
                        "获取失败",
                        f"处理失败: {str(e)}"
                    )
                    continue

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