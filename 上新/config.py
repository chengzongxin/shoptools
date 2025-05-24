# 浏览器配置
BROWSER_CONFIG = {
    'headless': False,  # 是否使用无头模式
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'window_size': (1920, 1080),  # 浏览器窗口大小
}

# 等待时间配置（秒）
WAIT_CONFIG = {
    'implicit_wait': 10,  # 隐式等待时间
    'explicit_wait': 20,  # 显式等待时间
}

# 调试模式
DEBUG = True 