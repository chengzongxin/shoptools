"""
事件通知系统使用示例代码

这个文件展示了如何在你的功能模块中集成事件通知系统
用于在网络请求发生403错误时自动停止任务
"""

import threading
import time
from typing import List

# 假设这些是从你的项目中导入的
# from ..network.request import NetworkRequest
# from ..network.event_manager import EventManager


# ============================================
# 示例1: 基础用法 - 在Crawler类中使用
# ============================================

class BasicCrawlerExample:
    """
    基础示例：如何在爬虫类中使用事件系统
    适合大多数简单的单线程场景
    """
    
    def __init__(self):
        # self.request = NetworkRequest()
        # self.event_manager = EventManager()
        
        # 任务停止标志
        self.should_stop = False
        
        # 订阅配置错误事件
        # self.event_manager.subscribe("config_error", self.on_config_error)
        print("[示例1] 已订阅 config_error 事件")
    
    def on_config_error(self, **kwargs):
        """
        当收到配置错误通知时调用
        
        参数说明:
            error_code: 错误代码（例如: 403）
            error_message: 详细错误信息
            request_type: 请求类型（GET/POST/PUT/DELETE）
        """
        error_code = kwargs.get('error_code')
        request_type = kwargs.get('request_type')
        error_message = kwargs.get('error_message', '').split('\n')[0]  # 只取第一行
        
        print(f"\n[示例1] ⚠️  收到配置错误通知!")
        print(f"  错误代码: {error_code}")
        print(f"  请求类型: {request_type}")
        print(f"  错误消息: {error_message}")
        print(f"[示例1] 正在停止任务...\n")
        
        # 设置停止标志
        self.should_stop = True
    
    def process_items(self, items: List[str]):
        """
        处理项目列表
        演示如何在循环中检查停止标志
        """
        print(f"[示例1] 开始处理 {len(items)} 个项目")
        
        for i, item in enumerate(items):
            # 🔑 关键点：在每次循环开始时检查停止标志
            if self.should_stop:
                print(f"[示例1] 任务已停止，已处理 {i}/{len(items)} 个项目")
                return
            
            # 处理项目
            print(f"[示例1] 处理项目 {i+1}/{len(items)}: {item}")
            time.sleep(0.5)  # 模拟处理时间
            
            # 发送网络请求
            # result = self.request.post("/api/process", {"item": item})
            # if result is None:
            #     # 如果是403错误，事件已经被触发，should_stop会被设置
            #     continue
        
        print(f"[示例1] 所有项目处理完成")


# ============================================
# 示例2: 多线程场景 - 使用threading.Event
# ============================================

class ThreadSafeCrawlerExample:
    """
    多线程示例：使用threading.Event实现线程安全的停止机制
    适合需要并发处理的场景
    """
    
    def __init__(self):
        # self.request = NetworkRequest()
        # self.event_manager = EventManager()
        
        # 使用 threading.Event 作为停止信号（线程安全）
        self.stop_event = threading.Event()
        
        # 订阅配置错误事件
        # self.event_manager.subscribe("config_error", self.on_config_error)
        print("[示例2] 已订阅 config_error 事件（线程安全版本）")
    
    def on_config_error(self, **kwargs):
        """配置错误处理函数"""
        print(f"\n[示例2] ⚠️  收到配置错误通知!")
        print(f"[示例2] 设置停止信号...\n")
        
        # 设置停止信号（线程安全）
        self.stop_event.set()
    
    def worker_thread(self, thread_id: int, items: List[str]):
        """
        工作线程函数
        演示如何在多线程中检查停止信号
        """
        print(f"[示例2-线程{thread_id}] 开始处理 {len(items)} 个项目")
        
        for i, item in enumerate(items):
            # 🔑 关键点：使用 is_set() 检查停止信号
            if self.stop_event.is_set():
                print(f"[示例2-线程{thread_id}] 检测到停止信号，已处理 {i}/{len(items)} 个项目")
                return
            
            print(f"[示例2-线程{thread_id}] 处理: {item}")
            time.sleep(0.3)
        
        print(f"[示例2-线程{thread_id}] 完成")
    
    def process_in_parallel(self, all_items: List[str], num_threads: int = 3):
        """
        并行处理项目
        """
        # 清除之前的停止信号
        self.stop_event.clear()
        
        # 将项目分配给不同线程
        chunk_size = len(all_items) // num_threads
        threads = []
        
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size if i < num_threads - 1 else len(all_items)
            items = all_items[start:end]
            
            thread = threading.Thread(
                target=self.worker_thread,
                args=(i+1, items)
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        print("[示例2] 所有线程已完成")


# ============================================
# 示例3: GUI集成 - 更新界面状态
# ============================================

class GUIIntegrationExample:
    """
    GUI集成示例：演示如何在GUI中响应配置错误事件
    注意：这里使用print模拟GUI更新，实际使用时替换为真实的GUI操作
    """
    
    def __init__(self):
        # self.event_manager = EventManager()
        
        # GUI状态
        self.status_text = "就绪"
        self.progress_value = 0
        
        # Crawler实例
        self.crawler = BasicCrawlerExample()
        
        # 订阅配置错误事件
        # self.event_manager.subscribe("config_error", self.on_config_error_gui)
        print("[示例3] GUI已订阅 config_error 事件")
    
    def on_config_error_gui(self, **kwargs):
        """
        GUI的配置错误处理函数
        更新界面状态并通知用户
        """
        print(f"\n[示例3-GUI] ⚠️  收到配置错误通知!")
        
        # 更新GUI状态
        self.status_text = "任务已停止：配置错误"
        # 实际代码：self.status_label.config(text=self.status_text, fg="red")
        print(f"[示例3-GUI] 状态更新: {self.status_text}")
        
        # 停止进度条
        # 实际代码：self.progress_bar.stop()
        print(f"[示例3-GUI] 进度条已停止")
        
        # 通知爬虫停止
        self.crawler.should_stop = True
        
        # 启用开始按钮，禁用停止按钮
        # 实际代码：
        # self.start_button.config(state="normal")
        # self.stop_button.config(state="disabled")
        print(f"[示例3-GUI] 按钮状态已更新\n")
    
    def start_task(self):
        """开始任务（通常是按钮点击事件）"""
        print("[示例3-GUI] 用户点击了'开始'按钮")
        
        # 重置停止标志
        self.crawler.should_stop = False
        
        # 更新GUI
        self.status_text = "正在运行..."
        print(f"[示例3-GUI] 状态: {self.status_text}")
        
        # 在新线程中运行任务
        items = [f"商品{i}" for i in range(1, 11)]
        thread = threading.Thread(
            target=self.crawler.process_items,
            args=(items,)
        )
        thread.start()


# ============================================
# 示例4: 实际场景 - 核价模块集成
# ============================================

class PriceReviewCrawlerExample:
    """
    实际场景示例：核价模块的完整集成
    展示了一个真实模块应该如何使用事件系统
    """
    
    def __init__(self):
        # self.request = NetworkRequest()
        # self.event_manager = EventManager()
        # self.logger = Logger()
        
        # 使用threading.Event作为停止信号
        self.stop_event = threading.Event()
        
        # 统计数据
        self.processed_count = 0
        self.success_count = 0
        self.fail_count = 0
        
        # 订阅配置错误事件
        # self.event_manager.subscribe("config_error", self._handle_config_error)
        print("[核价模块] 已初始化并订阅事件")
    
    def _handle_config_error(self, **kwargs):
        """
        处理配置错误事件
        这是一个私有方法，用下划线开头表示内部使用
        """
        error_code = kwargs.get('error_code', 'Unknown')
        request_type = kwargs.get('request_type', 'Unknown')
        
        # self.logger.error(f"收到配置错误通知: {error_code}")
        print(f"\n[核价模块] ❌ 收到配置错误通知")
        print(f"  错误代码: {error_code}")
        print(f"  请求类型: {request_type}")
        print(f"  已处理: {self.processed_count} 个商品")
        print(f"  成功: {self.success_count}")
        print(f"  失败: {self.fail_count}")
        print(f"[核价模块] 正在停止所有任务...\n")
        
        # 设置停止信号
        self.stop_event.set()
    
    def fetch_products_to_review(self, page_size: int = 100):
        """
        获取待核价商品列表
        """
        # 检查停止信号
        if self.stop_event.is_set():
            print("[核价模块] 任务已停止，取消获取商品")
            return []
        
        print(f"[核价模块] 正在获取待核价商品...")
        
        # 发送网络请求
        # result = self.request.post("/api/product/list", {"pageSize": page_size})
        # if result is None:
        #     return []
        
        # 模拟返回商品列表
        products = [f"商品-{i}" for i in range(1, 21)]
        print(f"[核价模块] 获取到 {len(products)} 个待核价商品")
        return products
    
    def review_single_product(self, product_id: str):
        """
        核价单个商品
        """
        # 检查停止信号
        if self.stop_event.is_set():
            return None
        
        print(f"[核价模块] 正在核价: {product_id}")
        
        # 发送核价请求
        # result = self.request.post("/api/product/review", {
        #     "productId": product_id,
        #     "action": "approve"
        # })
        
        # 模拟处理
        time.sleep(0.2)
        
        # if result is None:
        #     # 403错误，事件已触发
        #     return None
        
        # 模拟成功
        return {"status": "success", "productId": product_id}
    
    def batch_review(self):
        """
        批量核价 - 主要的业务逻辑方法
        """
        print("\n" + "="*50)
        print("[核价模块] 开始批量核价")
        print("="*50 + "\n")
        
        # 清除之前的停止信号
        self.stop_event.clear()
        
        # 重置统计
        self.processed_count = 0
        self.success_count = 0
        self.fail_count = 0
        
        # 获取商品列表
        products = self.fetch_products_to_review()
        
        if not products:
            print("[核价模块] 没有待核价商品")
            return
        
        # 处理每个商品
        for i, product in enumerate(products):
            # 🔑 每次循环都检查停止信号
            if self.stop_event.is_set():
                print(f"\n[核价模块] ⚠️  任务被中断")
                print(f"  已处理: {self.processed_count}/{len(products)} 个商品")
                break
            
            # 核价商品
            result = self.review_single_product(product)
            self.processed_count += 1
            
            if result:
                self.success_count += 1
            else:
                self.fail_count += 1
            
            # 每处理5个商品显示一次进度
            if (i + 1) % 5 == 0:
                print(f"[核价模块] 进度: {i+1}/{len(products)}")
        
        # 显示最终结果
        print(f"\n" + "="*50)
        print(f"[核价模块] 任务完成")
        print(f"  总计: {len(products)} 个商品")
        print(f"  已处理: {self.processed_count}")
        print(f"  成功: {self.success_count}")
        print(f"  失败: {self.fail_count}")
        print("="*50 + "\n")


# ============================================
# 测试代码
# ============================================

def test_basic_example():
    """测试基础示例"""
    print("\n" + "="*60)
    print("测试示例1: 基础用法")
    print("="*60 + "\n")
    
    crawler = BasicCrawlerExample()
    items = [f"项目-{i}" for i in range(1, 11)]
    
    # 模拟处理一会儿后触发错误
    def trigger_error():
        time.sleep(2)  # 等待2秒
        print("\n[模拟] 触发403错误...\n")
        crawler.on_config_error(error_code=403, request_type="POST", error_message="Cookie已过期")
    
    error_thread = threading.Thread(target=trigger_error)
    error_thread.start()
    
    crawler.process_items(items)
    error_thread.join()


def test_threadsafe_example():
    """测试多线程示例"""
    print("\n" + "="*60)
    print("测试示例2: 多线程场景")
    print("="*60 + "\n")
    
    crawler = ThreadSafeCrawlerExample()
    all_items = [f"项目-{i}" for i in range(1, 31)]
    
    # 模拟处理一会儿后触发错误
    def trigger_error():
        time.sleep(2)
        print("\n[模拟] 触发403错误...\n")
        crawler.on_config_error(error_code=403, request_type="GET", error_message="MallID配置错误")
    
    error_thread = threading.Thread(target=trigger_error)
    error_thread.start()
    
    crawler.process_in_parallel(all_items, num_threads=3)
    error_thread.join()


def test_price_review_example():
    """测试核价模块示例"""
    print("\n" + "="*60)
    print("测试示例4: 核价模块集成")
    print("="*60 + "\n")
    
    crawler = PriceReviewCrawlerExample()
    
    # 模拟处理一会儿后触发错误
    def trigger_error():
        time.sleep(3)
        print("\n[模拟] 触发403错误...\n")
        crawler._handle_config_error(
            error_code=403,
            request_type="POST",
            error_message="Cookie已过期，请更新系统配置"
        )
    
    error_thread = threading.Thread(target=trigger_error)
    error_thread.start()
    
    crawler.batch_review()
    error_thread.join()


if __name__ == "__main__":
    """
    运行所有测试示例
    你可以单独运行某个测试来查看效果
    """
    
    # 运行基础示例
    test_basic_example()
    time.sleep(1)
    
    # 运行多线程示例
    test_threadsafe_example()
    time.sleep(1)
    
    # 运行核价模块示例
    test_price_review_example()
    
    print("\n" + "="*60)
    print("所有示例测试完成!")
    print("="*60 + "\n")

