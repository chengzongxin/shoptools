from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from datetime import datetime
import os
from .price_mapper import PriceMapper
from ..common.logger import Logger

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
        self.logger = Logger("price", debug)
        
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

    def check_product_info_pending(self):
        """
        检查商品信息待确认按钮的状态，如果有待确认则点击取消选中
        :return: 是否有待确认的商品信息
        """
        try:
            if self.debug:
                print("正在检查商品信息待确认按钮状态...")

            # 使用XPath定位商品信息待确认按钮
            button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[1]/div[1]/div[2]/div[2]/div[1]/span[2]/span'))
            )
            
            # 获取按钮文本
            button_text = button.text
            
            if self.debug:
                print(f"商品信息待确认按钮状态: {button_text}")

            # 如果按钮文本包含数字，说明有待确认的商品信息
            if any(char.isdigit() for char in button_text):
                if self.debug:
                    print("发现有待确认的商品信息，点击按钮取消选中状态")
                # 点击父元素取消选中状态
                parent_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div[1]/div[1]/div[2]/div[2]/div[1]'))
                )
                parent_button.click()
                # 等待一下确保状态更新
                time.sleep(1)
                return True

            return False

        except Exception as e:
            print(f"检查商品信息待确认按钮状态失败: {str(e)}")
            return False

    def check_and_close_popup(self):
        """
        检查并关闭弹窗
        :return: 是否发现并关闭了弹窗
        """
        try:
            # 检查是否存在弹窗标题
            popup_title = self.driver.find_elements(By.CLASS_NAME, 'PP_popoverTitle_5-114-0')
            
            if popup_title:
                if self.debug:
                    print("发现弹窗，准备关闭...")
                
                # 点击关闭按钮
                close_button = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'new-bell_container__eWEgQ'))
                )
                close_button.click()
                
                # 等待弹窗消失
                time.sleep(1)
                
                if self.debug:
                    print("弹窗已关闭")
                
                return True
            
            return False

        except Exception as e:
            print(f"检查或关闭弹窗失败: {str(e)}")
            return False

    def set_page_size(self):
        """
        设置每页显示10条记录
        :return: 是否设置成功
        """
        try:
            if self.debug:
                print("正在设置每页显示数量...")

            # 点击分页输入框
            page_size_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[2]/div/div/div/div/div/div'))
            )
            page_size_input.click()
            
            # 等待下拉选项出现并点击"10"选项
            option_10 = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div/div/div/div/ul/li[1]'))
            )
            option_10.click()
            
            # 等待页面刷新
            time.sleep(2)
            
            if self.debug:
                print("已设置每页显示10条记录")
            
            return True

        except Exception as e:
            print(f"设置每页显示数量失败: {str(e)}")
            return False

    def click_price_pending_button(self):
        """
        点击价格待确认按钮
        """
        try:
            # 首先检查并关闭可能存在的弹窗
            self.check_and_close_popup()

            # 设置每页显示10条记录
            self.set_page_size()

            # 首先检查商品信息待确认按钮状态
            if self.check_product_info_pending():
                if self.debug:
                    print("发现有待确认的商品信息，请先处理商品信息待确认")

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
            
            return True

        except Exception as e:
            print(f"点击价格待确认按钮失败: {str(e)}")
            return False

    def get_page_info(self):
        """
        获取分页信息
        :return: (当前页码, 总页数, 每页数量)
        """
        try:
            # 等待分页组件加载
            pagination = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul'))
            )
            
            # 获取总条数
            total_items_element = pagination.find_element(By.XPATH, './li[1]')
            total_items_text = total_items_element.text
            total_items = int(''.join(filter(str.isdigit, total_items_text)))
            
            # 获取当前页码（通过class获取激活的页码）
            current_page_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.PGT_pagerItem_5-117-0.PGT_pagerItemActive_5-117-0'))
            )
            current_page = int(current_page_element.text)
            
            # 计算总页数（每页10条）
            total_pages = (total_items + 9) // 10  # 向上取整
            
            if self.debug:
                print(f"分页信息: 总条数 {total_items}, 当前页 {current_page}/{total_pages}, 每页 10 条")
            
            return current_page, total_pages, 10  # 固定返回每页10条
            
        except Exception as e:
            print(f"获取分页信息失败: {str(e)}")
            return 1, 100, 10  # 默认值改为每页10条

    def go_to_next_page(self):
        """
        跳转到下一页，如果已经是最后一页则返回第一页
        :return: 是否成功跳转
        """
        try:
            # 等待分页组件加载
            pagination = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul'))
            )
            
            try:
                # 在分页组件中查找下一页按钮
                next_button = pagination.find_element(By.CLASS_NAME, 'PGT_next_5-117-0')
                
                # 确保按钮可点击
                self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'PGT_next_5-117-0')))
                
                # 点击下一页按钮
                next_button.click()
                
                if self.debug:
                    print("已跳转到下一页")
                
                return True
                
            except Exception as e:
                if self.debug:
                    print("已到达最后一页，准备返回第一页")
                
                # 点击第一页按钮
                first_page_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[4]'))
                )
                first_page_button.click()
                
                # 等待页面加载
                time.sleep(2)
                
                if self.debug:
                    print("已返回第一页")
                
                return True
            
        except Exception as e:
            print(f"页面跳转失败: {str(e)}")
            return False

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
            
            # 获取所有商品行
            rows = product_list.find_elements(By.TAG_NAME, "tr")
            
            # 确保索引在有效范围内
            if 0 <= index - 1 < len(rows):
                if self.debug:
                    print(f"成功获取第 {index} 行元素")
                return rows[index - 1]
            else:
                if self.debug:
                    print(f"索引 {index} 超出范围，总行数: {len(rows)}")
                return None
                
        except Exception as e:
            print(f"获取第 {index} 行元素失败: {str(e)}")
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

            # 1. 等待弹窗出现
            modal = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "MDL_innerWrapper_5-111-0"))
            )
            
            # 2. 获取新申报价格
            price_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".TB_whiteTr_5-111-0 td:nth-child(5) span:nth-child(2)"))
            )
            new_price = float(price_element.text)
            
            if self.debug:
                print(f"最低核价: {min_price}")
                print(f"新申报价格: {new_price}")

            # 比较价格
            if new_price > min_price:
                if self.debug:
                    print("新申报价格大于最低核价，直接确认")
                
                # 3. 点击确认按钮
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".MDL_okBtn_5-111-0"))
                )


                time.sleep(1000)

                confirm_button.click()
                
                # 记录日志
                self.log_record(sku, spu, min_price, new_price, "确认提交")
                
            else:
                if self.debug:
                    print("新申报价格小于等于最低核价，选择放弃调整报价")
                
                # 4. 点击下拉框
                dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#operatorType .ST_head_5-111-0"))
                )
                dropdown.click()
                
                # 5. 选择"放弃调整报价"选项
                abandon_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ST_option_5-111-0')]//span[contains(text(), '放弃调整报价')]"))
                )
                abandon_option.click()

                # 6. 点击确认按钮
                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".MDL_okBtn_5-111-0"))
                )

                time.sleep(1000)

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
            # 获取元素位置
            element_location = element.location
            element_size = element.size
            
            # 计算元素中心点
            element_center = element_location['y'] + element_size['height'] / 2
            
            # 获取视窗高度
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # 计算需要滚动的距离
            scroll_distance = element_center - viewport_height / 2
            
            # 使用JavaScript平滑滚动
            self.driver.execute_script(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
            
            # 等待滚动完成
            time.sleep(1)
            
            if self.debug:
                print(f"已滚动到元素位置，滚动距离: {scroll_distance}px")
                
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
            
            # 获取所有商品行
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
            current_page = 1
            while True:
                # 获取分页信息
                current_page, total_pages, items_per_page = self.get_page_info()
                
                if self.debug:
                    print(f"\n开始处理第 {current_page}/{total_pages} 页")

                # 获取当前页的所有商品行
                product_list = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div > div > div.TB_outerWrapper_5-117-0.TB_bordered_5-117-0.TB_notTreeStriped_5-117-0 > div.TB_inner_5-117-0 > div > div.TB_body_5-117-0 > div > div > table > tbody'))
                )
                rows = product_list.find_elements(By.TAG_NAME, "tr")

                # 处理当前页的每一行商品
                for index, row in enumerate(rows, 1):
                    try:
                        if self.debug:
                            print(f"\n处理第 {index} 个商品:")
                        
                        # 滚动到当前商品位置
                        self.scroll_to_element(row)
                        
                        # 获取商品信息
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

                # 检查是否需要翻页
                if current_page < total_pages:
                    if not self.go_to_next_page():
                        print("无法跳转到下一页，处理结束")
                        break
                    # 等待页面加载
                    time.sleep(2)
                else:
                    if self.debug:
                        print("已处理完所有页面，准备重新从第一页开始检查")
                    
                    # 点击第一页按钮
                    first_page_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[4]'))
                    )
                    first_page_button.click()
                    
                    # 等待页面加载
                    time.sleep(2)
                    
                    # 重新获取分页信息
                    current_page, total_pages, items_per_page = self.get_page_info()
                    
                    if self.debug:
                        print("已返回第一页，开始第二轮检查")
                    
                    # 继续处理第一页
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