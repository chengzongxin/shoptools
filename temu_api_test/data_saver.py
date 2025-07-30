#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据保存模块
用于将API响应数据保存到JSON文件中
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataSaver:
    """数据保存类"""
    
    def __init__(self, output_dir: str = "data"):
        """
        初始化数据保存器
        
        Args:
            output_dir (str): 输出目录，默认为 "data"
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self) -> None:
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"📁 创建输出目录: {self.output_dir}")
    
    def save_response(self, data: Dict[str, Any], page: int, timestamp: str = None) -> str:
        """
        保存API响应数据
        
        Args:
            data (Dict[str, Any]): API响应数据
            page (int): 页码
            timestamp (str): 时间戳，如果为None则自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成文件名
        filename = f"temu_products_page_{page}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # 保存数据到JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 数据已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
            return ""
    
    def save_products_summary(self, all_products: List[Dict[str, Any]], timestamp: str = None) -> str:
        """
        保存产品数据摘要
        
        Args:
            all_products (List[Dict[str, Any]]): 所有产品数据列表
            timestamp (str): 时间戳，如果为None则自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成摘要文件名
        filename = f"temu_products_summary_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 构建摘要数据
        summary = {
            "timestamp": timestamp,
            "total_products": len(all_products),
            "products": all_products
        }
        
        try:
            # 保存摘要数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 产品摘要已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 保存产品摘要失败: {e}")
            return ""
    
    def extract_products_from_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从API响应中提取产品数据
        
        Args:
            response_data (Dict[str, Any]): API响应数据
            
        Returns:
            List[Dict[str, Any]]: 产品数据列表
        """
        products = []
        
        try:
            # 检查响应结构
            if response_data.get('success') and 'result' in response_data:
                result = response_data['result']
                
                # 提取产品列表
                if 'pageItems' in result:
                    products = result['pageItems']
                    logger.info(f"📦 提取到 {len(products)} 个产品")
                else:
                    logger.warning("⚠️ 响应中没有找到 pageItems 字段")
            else:
                logger.warning("⚠️ 响应格式不符合预期")
                
        except Exception as e:
            logger.error(f"❌ 提取产品数据失败: {e}")
        
        return products
    
    def save_csv_summary(self, all_products: List[Dict[str, Any]], timestamp: str = None) -> str:
        """
        保存CSV格式的产品摘要
        
        Args:
            all_products (List[Dict[str, Any]]): 所有产品数据列表
            timestamp (str): 时间戳，如果为None则自动生成
            
        Returns:
            str: 保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成CSV文件名
        filename = f"temu_products_summary_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            import csv
            
            # 定义CSV字段
            fieldnames = [
                'productId', 'productSkcId', 'productName', 'productType', 
                'sourceType', 'goodsId', 'catName', 'cat1Name', 'cat2Name', 'cat3Name'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in all_products:
                    # 提取需要的数据
                    row = {
                        'productId': product.get('productId', ''),
                        'productSkcId': product.get('productSkcId', ''),
                        'productName': product.get('productName', ''),
                        'productType': product.get('productType', ''),
                        'sourceType': product.get('sourceType', ''),
                        'goodsId': product.get('goodsId', ''),
                        'catName': product.get('leafCat', {}).get('catName', ''),
                        'cat1Name': product.get('categories', {}).get('cat1', {}).get('catName', ''),
                        'cat2Name': product.get('categories', {}).get('cat2', {}).get('catName', ''),
                        'cat3Name': product.get('categories', {}).get('cat3', {}).get('catName', '')
                    }
                    writer.writerow(row)
            
            logger.info(f"📊 CSV摘要已保存到: {filepath}")
            return filepath
            
        except ImportError:
            logger.error("❌ 需要安装csv模块")
            return ""
        except Exception as e:
            logger.error(f"❌ 保存CSV摘要失败: {e}")
            return ""

def main():
    """测试数据保存功能"""
    # 创建数据保存器
    saver = DataSaver()
    
    # 测试数据
    test_data = {
        "success": True,
        "errorCode": 1000000,
        "errorMsg": None,
        "result": {
            "total": 100,
            "pageItems": [
                {
                    "productId": 123456,
                    "productName": "测试产品",
                    "productType": 1
                }
            ]
        }
    }
    
    # 保存测试数据
    filepath = saver.save_response(test_data, 1)
    print(f"测试数据已保存到: {filepath}")

if __name__ == "__main__":
    main() 