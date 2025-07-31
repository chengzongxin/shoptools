"""
WebSocket Cookie获取模块 - 全局对象版本
通过WebSocket与Chrome插件通信获取Cookie
"""

import asyncio
import json
import logging
import queue
import threading
import time
import websockets
from typing import Dict, List, Optional, Tuple

# 全局变量
connected_clients: List = []
command_queue = queue.Queue()
response_queue = queue.Queue()
is_running = False
server_thread = None
host = "localhost"
port = 8765

# 日志记录器
logger = None

def setup_logger():
    """设置日志记录器"""
    global logger
    if logger is not None:
        return logger
    
    logger = logging.getLogger("WebSocketCookie")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[WebSocket] %(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 防止日志传播到GUI
    logger.propagate = False
    
    return logger

async def handle_client(websocket):
    """处理客户端连接"""
    global connected_clients, logger
    
    if logger is None:
        logger = setup_logger()
    
    client_id = f"client_{len(connected_clients)}"
    connected_clients.append(websocket)
    logger.info(f"Chrome插件已连接: {client_id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"收到消息: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'command_response':
                    # 处理来自插件的命令响应
                    logger.info(f"收到插件响应: {data.get('data', {})}")
                    response_queue.put(data)
                    # 不需要回复，只记录响应
                    continue
                elif data.get('type') == 'greeting':
                    # 回应问候消息
                    response = {
                        'type': 'response',
                        'message': f"你好！我收到了你的消息: {data.get('content', '')}"
                    }
                elif data.get('type') == 'text':
                    # 处理自定义文本消息
                    text_content = data.get('content', '')
                    response = {
                        'type': 'response',
                        'message': f"收到文本消息: {text_content}",
                        'echo': text_content
                    }
                else:
                    # 默认回应
                    response = {
                        'type': 'echo',
                        'original_message': data,
                        'timestamp': str(asyncio.get_event_loop().time())
                    }
                
                # 发送回应消息
                await websocket.send(json.dumps(response, ensure_ascii=False))
                logger.info(f"已发送回应: {response}")
                    
            except json.JSONDecodeError:
                logger.error(f"无效的JSON消息: {message}")
                # 发送错误响应
                error_response = {
                    'type': 'error',
                    'message': '无效的JSON格式'
                }
                await websocket.send(json.dumps(error_response, ensure_ascii=False))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"客户端断开连接: {client_id}")
    except Exception as e:
        logger.error(f"处理客户端消息时出错: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        logger.info(f"客户端已移除: {client_id}")

async def broadcast_message(message):
    """广播消息到所有连接的客户端"""
    global connected_clients, logger
    
    if logger is None:
        logger = setup_logger()
    
    if not connected_clients:
        logger.warning("没有连接的客户端")
        return
    
    # 转换为JSON字符串
    if isinstance(message, dict):
        message = json.dumps(message)
    
    # 发送到所有客户端
    for client in connected_clients[:]:  # 使用副本避免修改迭代中的列表
        try:
            await client.send(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            if client in connected_clients:
                connected_clients.remove(client)

async def send_command_to_plugin(command):
    """发送命令到Chrome插件"""
    global logger
    
    if logger is None:
        logger = setup_logger()
    
    if not connected_clients:
        logger.warning("没有连接的Chrome插件")
        return False
    
    try:
        # 按照websocket_server.py的格式发送命令
        message = {
            'type': 'backend_command',
            'command': command.get('action'),
            'params': command.get('params', {}),
            'command_id': command.get('command_id', f"cmd_{int(time.time())}")
        }
        await broadcast_message(message)
        logger.info(f"命令已发送: {command.get('action', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"发送命令失败: {e}")
        return False

async def command_handler():
    """命令处理器"""
    global command_queue, logger
    
    if logger is None:
        logger = setup_logger()
    
    logger.info("命令处理器已启动")
    
    while is_running:
        try:
            # 非阻塞方式检查命令队列
            try:
                command = command_queue.get_nowait()
                await send_command_to_plugin(command)
            except queue.Empty:
                pass
            
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"命令处理器错误: {e}")
            await asyncio.sleep(1)

async def websocket_server():
    """WebSocket服务器主函数"""
    global logger
    
    if logger is None:
        logger = setup_logger()
    
    try:
        logger.info(f"WebSocket服务器启动中...")
        logger.info(f"监听地址: ws://{host}:{port}")
        
        # 直接使用全局函数，避免类方法绑定问题
        async with websockets.serve(handle_client, host, port):
            logger.info("WebSocket服务器已启动")
            await command_handler()
    except Exception as e:
        logger.error(f"WebSocket服务器错误: {e}")

def run_websocket_server():
    """在单独线程中运行WebSocket服务器"""
    asyncio.run(websocket_server())

def start_server():
    """启动WebSocket服务器"""
    global is_running, server_thread, logger
    
    if logger is None:
        logger = setup_logger()
    
    if is_running:
        logger.warning("WebSocket服务器已在运行")
        return
    
    is_running = True
    server_thread = threading.Thread(target=run_websocket_server, daemon=True)
    server_thread.start()
    logger.info("WebSocket服务器启动中...")

def stop_server():
    """停止WebSocket服务器"""
    global is_running, logger
    
    if logger is None:
        logger = setup_logger()
    
    is_running = False
    logger.info("WebSocket服务器已停止")

def wait_for_response(timeout=10):
    """等待插件响应"""
    try:
        response = response_queue.get(timeout=timeout)
        # 按照websocket_server.py的格式，响应数据在'data'字段中
        return response.get('data', {})
    except queue.Empty:
        return None

def send_command(action, params=None):
    """发送命令到Chrome插件并等待响应"""
    global connected_clients, logger
    
    if logger is None:
        logger = setup_logger()
    
    if not connected_clients:
        logger.warning("没有连接的Chrome插件")
        return None
    
    command_id = f"cmd_{int(time.time())}"
    command = {
        'action': action,
        'params': params or {},
        'command_id': command_id
    }
    
    # 清空响应队列
    while not response_queue.empty():
        response_queue.get_nowait()
    
    # 发送命令
    command_queue.put(command)
    logger.info(f"发送命令: {action}")
    
    # 等待响应
    response = wait_for_response()
    
    if response:
        logger.info("收到插件响应")
        return response
    else:
        logger.warning("响应超时")
        return None

def get_domain_cookies(domain: str) -> Tuple[str, str]:
    """
    获取指定域名的Cookie
    
    Returns:
        tuple: (cookie_string, error_message)
    """
    global logger
    
    if logger is None:
        logger = setup_logger()
    
    try:
        logger.info(f"获取域名 '{domain}' 的Cookie...")
        response = send_command('get_cookies_by_domain', {'domain': domain})
        
        if response and response.get('success'):
            cookies = response.get('cookies', [])
            logger.info(f"找到 {len(cookies)} 个Cookie")
            
            # 格式化Cookie
            formatted_cookies = "; ".join([
                f"{cookie.get('name', '')}={cookie.get('value', '')}" 
                for cookie in cookies
            ])
            
            if formatted_cookies:
                return formatted_cookies, ""
            else:
                return "", "未找到有效的Cookie"
        else:
            error_msg = response.get('error', '未知错误') if response else '响应超时'
            return "", f"获取Cookie失败: {error_msg}"
            
    except Exception as e:
        error_msg = f"获取Cookie时发生异常: {str(e)}"
        logger.error(error_msg)
        return "", error_msg

def get_domain_requests(domain: str) -> Tuple[List, str]:
    """
    获取指定域名的拦截请求
    
    Returns:
        tuple: (requests_list, error_message)
    """
    global logger
    
    if logger is None:
        logger = setup_logger()
    
    try:
        logger.info(f"获取域名 '{domain}' 的拦截请求...")
        response = send_command('get_requests_by_domain', {'domain': domain})
        
        if response and response.get('success'):
            requests = response.get('requests', [])
            logger.info(f"找到 {len(requests)} 个请求")
            return requests, ""
        else:
            error_msg = response.get('error', '未知错误') if response else '响应超时'
            return [], f"获取请求失败: {error_msg}"
            
    except Exception as e:
        error_msg = f"获取请求时发生异常: {str(e)}"
        logger.error(error_msg)
        return [], error_msg

def get_requests_by_header(header_name: str, header_value: str = None) -> Tuple[List, str]:
    """
    根据请求头查询拦截的请求
    
    Returns:
        tuple: (requests_list, error_message)
    """
    global logger
    
    if logger is None:
        logger = setup_logger()
    
    try:
        logger.info(f"查询包含请求头 '{header_name}' 的请求...")
        params = {'headerName': header_name}
        if header_value:
            params['headerValue'] = header_value
        
        response = send_command('find_requests_by_header', params)
        
        if response and response.get('success'):
            requests = response.get('requests', [])
            logger.info(f"找到 {len(requests)} 个匹配的请求")
            return requests, ""
        else:
            error_msg = response.get('error', '未知错误') if response else '响应超时'
            return [], f"查询请求失败: {error_msg}"
            
    except Exception as e:
        error_msg = f"查询请求时发生异常: {str(e)}"
        logger.error(error_msg)
        return [], error_msg

def is_connected() -> bool:
    """检查是否有连接的客户端"""
    return len(connected_clients) > 0

# 兼容性接口 - 保持与原有代码的兼容性
class WebSocketCookieManager:
    """兼容性包装类"""
    
    def __init__(self):
        pass
    
    def start_server(self):
        start_server()
    
    def stop_server(self):
        stop_server()
    
    def get_domain_cookies(self, domain: str) -> Tuple[str, str]:
        return get_domain_cookies(domain)
    
    def get_domain_requests(self, domain: str) -> Tuple[List, str]:
        return get_domain_requests(domain)
    
    def get_requests_by_header(self, header_name: str, header_value: str = None) -> Tuple[List, str]:
        return get_requests_by_header(header_name, header_value)
    
    def is_connected(self) -> bool:
        return is_connected()
    
    @property
    def connected_clients(self):
        return connected_clients
    
    @property
    def is_running(self):
        return is_running

def get_websocket_manager() -> WebSocketCookieManager:
    """获取WebSocket管理器（兼容性接口）"""
    return WebSocketCookieManager()

def start_websocket_server():
    """启动WebSocket服务器（兼容性接口）"""
    start_server()

def stop_websocket_server():
    """停止WebSocket服务器（兼容性接口）"""
    stop_server()