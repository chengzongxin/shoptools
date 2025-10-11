"""
事件管理器模块
用于处理应用程序中的事件发布和订阅机制
"""

from typing import Callable, Dict, List
import threading

class EventManager:
    """
    事件管理器类 - 实现观察者模式
    
    这个类就像一个"广播电台"：
    - 某个模块可以"发布"（publish）一个事件（比如发生了403错误）
    - 其他模块可以"订阅"（subscribe）这个事件，当事件发生时会收到通知
    
    使用场景：
    当网络请求发生403错误时，通知所有正在运行的任务停止工作
    """
    
    # 使用单例模式，确保整个应用程序只有一个事件管理器实例
    _instance = None
    _lock = threading.Lock()  # 线程锁，确保线程安全
    
    def __new__(cls):
        """
        单例模式的实现
        无论创建多少次EventManager对象，都返回同一个实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 初始化订阅者字典
                    # 格式: {"事件名称": [回调函数1, 回调函数2, ...]}
                    cls._instance._subscribers = {}
        return cls._instance
    
    def subscribe(self, event_name: str, callback: Callable):
        """
        订阅事件
        
        参数:
            event_name: 事件名称（例如："config_error"）
            callback: 回调函数，当事件发生时会被调用
        
        示例:
            def on_config_error():
                print("收到配置错误通知，停止任务")
            
            event_manager = EventManager()
            event_manager.subscribe("config_error", on_config_error)
        """
        # 如果这个事件还没有订阅者列表，创建一个空列表
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        # 将回调函数添加到订阅者列表中
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
            print(f"[事件管理器] 新订阅者已注册: 事件='{event_name}', 回调={callback.__name__}")
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """
        取消订阅事件
        
        参数:
            event_name: 事件名称
            callback: 要移除的回调函数
        
        示例:
            event_manager.unsubscribe("config_error", on_config_error)
        """
        if event_name in self._subscribers:
            if callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)
                print(f"[事件管理器] 订阅者已移除: 事件='{event_name}', 回调={callback.__name__}")
    
    def publish(self, event_name: str, **kwargs):
        """
        发布事件 - 通知所有订阅者
        
        参数:
            event_name: 事件名称
            **kwargs: 传递给回调函数的额外参数
        
        示例:
            event_manager.publish("config_error", error_code=403, message="Cookie已过期")
        """
        if event_name in self._subscribers:
            print(f"[事件管理器] 发布事件: '{event_name}', 订阅者数量: {len(self._subscribers[event_name])}")
            
            # 调用所有订阅了这个事件的回调函数
            for callback in self._subscribers[event_name]:
                try:
                    # 执行回调函数，传递额外参数
                    callback(**kwargs)
                except Exception as e:
                    # 如果某个回调函数出错，不影响其他回调函数的执行
                    print(f"[事件管理器] 回调函数执行出错: {callback.__name__}, 错误: {str(e)}")
        else:
            print(f"[事件管理器] 发布事件: '{event_name}', 但没有订阅者")
    
    def clear_all(self):
        """
        清空所有订阅者
        通常在程序退出时调用
        """
        self._subscribers.clear()
        print("[事件管理器] 所有订阅者已清空")
    
    def get_subscribers_count(self, event_name: str) -> int:
        """
        获取某个事件的订阅者数量
        
        参数:
            event_name: 事件名称
        
        返回:
            订阅者数量
        """
        if event_name in self._subscribers:
            return len(self._subscribers[event_name])
        return 0

