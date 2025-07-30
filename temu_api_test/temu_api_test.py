#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temu API 测试脚本
用于测试 Temu 代理商产品查询接口
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
import logging
from data_saver import DataSaver

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('temu_api_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TemuAPITester:
    """Temu API 测试类"""
    
    def __init__(self):
        """初始化测试类"""
        # 目标接口URL
        self.base_url = "https://agentseller.temu.com"
        self.api_endpoint = "/visage-agent-seller/product/skc/pageQuery"
        
        # 创建会话对象，用于保持连接和cookie
        self.session = requests.Session()
        
        # 创建数据保存器
        self.data_saver = DataSaver()
        
        # 存储所有产品数据
        self.all_products = []
        
        # 设置请求头（从浏览器中复制的完整请求头）
        self.headers = {
            # 基础请求头
            "authority": "agentseller.temu.com",
            "method": "POST",
            "path": "/visage-agent-seller/product/skc/pageQuery",
            "scheme": "https",
            
            # 接受类型
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            
            # 缓存控制
            "cache-control": "max-age=0",
            "content-type": "application/json",
            
            # Cookie（重要！包含登录状态和认证信息）
            "cookie": "api_uid=CmysKGgbCAqdegBhOAazAg==; _bee=nHN7phQkttiBUQZxm5dBMijzREKBSanV; njrpl=nHN7phQkttiBUQZxm5dBMijzREKBSanV; dilx=jWhDSdH9veu-pFQDJUjXI; hfsc=L3yOfo8w6Dfx2pPNeg==; user_uin=BBIABSJYQPS3VPJMRV4D2IW42BNXULBVJ2N4OVEB; _nano_fp=XpmYnqCaX0TJnqdoXT_ojTDNzKAZ~jgQfrU52AVm; mallid=634418223796259; AccessToken=ES4GERIQF4ZTB3KUGHPNK3I55J3IAHDIOVUSJ33JR6SO73PGCMWQ01102531f251; isLogin=1751620498159; seller_temp=N_eyJ0IjoidE1RS0FUQVQ4TEptRkdpK2pneGc0b3gwZkJvRk1TS0RUUWRTZUtvNGVuZVRoTkxZSEgyeFBCZ1ZTNEZEWDRLUXh3M1BBdmkydm9lTkswZEdiS0V3akE9PSIsInYiOjEsInMiOjEwMDAxLCJ1IjoyNDE1MTU0NjgxNzcwMX0=",
            
            # 商城ID
            "mallid": "634418223796259",
            
            # 来源和引用
            "origin": "https://agentseller.temu.com",
            "referer": "https://agentseller.temu.com/goods/list",
            
            # 优先级
            "priority": "u=1, i",
            
            # 安全相关头部
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            
            # 用户代理
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        
        # 将请求头应用到会话中
        self.session.headers.update(self.headers)
        
        logger.info("Temu API 测试器初始化完成")
    
    def test_api_connection(self) -> bool:
        """
        测试API连接是否正常
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 发送一个简单的GET请求到基础URL，测试连接
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ API连接测试成功")
                return True
            else:
                logger.warning(f"⚠️ API连接测试返回状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API连接测试失败: {e}")
            return False
    
    def query_products(self, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        查询产品数据
        
        Args:
            page (int): 页码，默认为1
            page_size (int): 每页数量，默认为20
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        # 构建请求URL
        url = f"{self.base_url}{self.api_endpoint}"
        
        # 构建请求参数
        payload = {
            "page": page,
            "pageSize": page_size
        }
        
        try:
            logger.info(f"🔄 正在查询第 {page} 页，每页 {page_size} 条数据...")
            
            # 发送POST请求
            response = self.session.post(
                url=url,
                json=payload,  # 使用json参数自动设置Content-Type和序列化数据
                timeout=30
            )
            
            # 记录响应状态
            logger.info(f"📊 响应状态码: {response.status_code}")
            logger.info(f"📊 响应头: {dict(response.headers)}")
            
            # 检查响应状态码
            if response.status_code == 200:
                # 尝试解析JSON响应
                try:
                    data = response.json()
                    logger.info("✅ 数据查询成功")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON解析失败: {e}")
                    logger.error(f"❌ 响应内容: {response.text[:500]}...")
                    return None
            else:
                logger.error(f"❌ 请求失败，状态码: {response.status_code}")
                logger.error(f"❌ 响应内容: {response.text[:500]}...")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 请求异常: {e}")
            return None
    
    def analyze_response(self, data: Dict[str, Any], page: int) -> None:
        """
        分析响应数据
        
        Args:
            data (Dict[str, Any]): 响应数据
            page (int): 页码
        """
        logger.info("🔍 开始分析响应数据...")
        
        # 保存原始响应数据
        self.data_saver.save_response(data, page)
        
        # 提取产品数据
        products = self.data_saver.extract_products_from_response(data)
        self.all_products.extend(products)
        
        # 打印数据结构
        logger.info(f"📋 响应数据类型: {type(data)}")
        logger.info(f"📋 响应数据键: {list(data.keys())}")
        
        # 检查常见字段
        if isinstance(data, dict):
            # 检查是否有错误信息
            if 'error' in data:
                logger.error(f"❌ 接口返回错误: {data['error']}")
            
            # 检查是否有成功标识
            if 'success' in data:
                logger.info(f"✅ 成功标识: {data['success']}")
            
            # 检查是否有结果字段
            if 'result' in data:
                result = data['result']
                logger.info(f"📊 结果字段类型: {type(result)}")
                
                if isinstance(result, dict):
                    logger.info(f"📊 结果字段键: {list(result.keys())}")
                    
                    # 检查产品列表
                    if 'pageItems' in result:
                        products = result['pageItems']
                        logger.info(f"📦 产品数量: {len(products) if isinstance(products, list) else '非列表类型'}")
                        
                        # 显示前几个产品的信息
                        if isinstance(products, list) and products:
                            logger.info("📦 前3个产品信息:")
                            for i, product in enumerate(products[:3]):
                                product_name = product.get('productName', '未知产品')
                                product_id = product.get('productId', '未知ID')
                                logger.info(f"   产品 {i+1}: ID={product_id}, 名称={product_name[:50]}...")
                    
                    # 检查分页信息
                    if 'total' in result:
                        logger.info(f"📄 总记录数: {result['total']}")
            
            # 打印完整响应（限制长度）
            response_str = json.dumps(data, ensure_ascii=False, indent=2)
            if len(response_str) > 1000:
                logger.info(f"📄 完整响应（前1000字符）:\n{response_str[:1000]}...")
            else:
                logger.info(f"📄 完整响应:\n{response_str}")
        else:
            logger.warning(f"⚠️ 响应数据不是字典类型: {type(data)}")
    
    def run_test(self, pages: int = 3) -> None:
        """
        运行完整的测试流程
        
        Args:
            pages (int): 要测试的页数
        """
        logger.info("🚀 开始运行Temu API测试...")
        
        # 1. 测试连接
        if not self.test_api_connection():
            logger.error("❌ 连接测试失败，停止测试")
            return
        
        # 2. 测试多页数据查询
        for page in range(1, pages + 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"📄 测试第 {page} 页")
            logger.info(f"{'='*50}")
            
            # 查询数据
            data = self.query_products(page=page, page_size=20)
            
            if data:
                # 分析响应
                self.analyze_response(data, page)
            else:
                logger.error(f"❌ 第 {page} 页查询失败")
            
            # 添加延迟，避免请求过于频繁
            if page < pages:
                logger.info("⏳ 等待2秒后继续...")
                time.sleep(2)
        
        # 保存所有产品数据的摘要
        if self.all_products:
            logger.info(f"\n📊 总共获取到 {len(self.all_products)} 个产品")
            self.data_saver.save_products_summary(self.all_products)
            self.data_saver.save_csv_summary(self.all_products)
        
        logger.info("\n🎉 测试完成！")

def main():
    """主函数"""
    print("=" * 60)
    print("🛍️ Temu API 测试脚本")
    print("=" * 60)
    
    # 创建测试器实例
    tester = TemuAPITester()
    
    # 运行测试
    tester.run_test(pages=2)  # 测试2页数据
    
    print("\n📝 测试日志已保存到 temu_api_test.log 文件中")

if __name__ == "__main__":
    main() 