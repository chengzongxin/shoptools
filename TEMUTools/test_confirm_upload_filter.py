#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试确认上新时间过滤功能
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.modules.confirm_upload.crawler import ConfirmUploadCrawler
from src.system_config.config import SystemConfig

def test_time_filter():
    """测试时间过滤功能"""
    print("=== 测试确认上新时间过滤功能 ===")
    
    # 获取配置
    config = SystemConfig()
    cookie = config.get_seller_cookie()
    
    if not cookie:
        print("❌ 请先在系统配置中设置Cookie")
        return
    
    # 创建爬虫实例
    crawler = ConfirmUploadCrawler(
        cookie=cookie,
        logger=None,
        progress_callback=None,
        stop_flag_callback=None
    )
    
    # 测试不同的过滤天数
    test_days = [1, 3, 5, 7]
    
    for days in test_days:
        print(f"\n--- 测试过滤 {days} 天 ---")
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        time_begin = int(start_time.timestamp() * 1000)
        time_end = int(end_time.timestamp() * 1000)
        
        print(f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"时间戳: {time_begin} 到 {time_end}")
        
        # 构建请求参数
        payload = {
            "pageSize": 10,
            "pageNum": 1,
            "timeType": 1,
            "timeBegin": time_begin,
            "timeEnd": time_end,
            "supplierTodoTypeList": [6]
        }
        
        print(f"请求参数: {payload}")
        
        # 发送请求
        try:
            result = crawler.request.post(crawler.api_url, data=payload)
            
            if result and result.get('success'):
                items = result.get('result', {}).get('dataList', [])
                print(f"✅ 成功获取 {len(items)} 条数据")
                
                # 显示前3条数据的创建时间
                for i, item in enumerate(items[:3]):
                    created_at = item.get('productCreatedAt', 0)
                    if created_at:
                        created_time = datetime.fromtimestamp(created_at/1000).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  商品 {i+1}: {created_time}")
            else:
                print(f"❌ 请求失败: {result.get('errorMsg', '未知错误') if result else '无返回'}")
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_time_filter() 