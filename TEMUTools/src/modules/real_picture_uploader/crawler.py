import logging
import time
import random
import os
import requests
import sys
from typing import List, Dict, Any, Optional
from ..network.request import NetworkRequest
from ..config.config import category_config

class RealPictureUploader:
    """
    实拍图批量上传核心逻辑
    """
    def __init__(self, logger: logging.Logger, progress_callback=None, stop_flag_callback=None):
        self.logger = logger
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback or (lambda: False)
        self.request = NetworkRequest()
        
        # 基础URL
        self.base_url = "https://agentseller.temu.com"
        self.list_url = f"{self.base_url}/api/flash/real_picture/list"
        self.signature_url = f"{self.base_url}/ms/bg-flux-ms/compliance_property/signature"
        self.upload_url = f"{self.base_url}/api/galerie/v3/store_image"
        self.batch_upload_url = f"{self.base_url}/api/flash/real_picture/batch_upload"
        
        # 从全局配置获取品类配置
        self.categories = category_config.get_categories()
        
        # 图片文件路径
        if getattr(sys, 'frozen', False):
            # The application is frozen (packaged)
            base_path = sys._MEIPASS
        else:
            # The application is running from source
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        self.images_dir = os.path.join(base_path, 'assets', 'images')
        
    def random_delay(self, min_sec=0, max_sec=1):
        """随机延迟，模拟人工操作"""
        delay = random.uniform(min_sec, max_sec)
        self.logger.info(f"随机延时 {delay:.2f} 秒")
        time.sleep(delay)
        
    def get_pending_products(self, category: Dict[str, Any], page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
        """
        获取未上传实拍图的商品列表
        """
        self.random_delay()
        
        # payload = {
        #     "page": page,
        #     "page_size": page_size,
        #     "need_on_sale": True,
        #     "from_batch_upload": True,
        #     "spu_id_list": [],
        #     "cate_id_list": [category["cate_id"]],
        #     "have_upload": False
        # }

        payload = {
            "page": page,
            "page_size": page_size,
            "cate_id_list": [category["cate_id"]],
            "check_type_status_list": [1],
            "rapid_screen_status_list": [1]
        }
        
        self.logger.info(f"查询 {category['name']} 未上传商品，第 {page} 页")
        self.logger.debug(f"请求参数: {payload}")
        
        resp = self.request.post(self.list_url, payload)
        
        if not resp or not resp.get("success"):
            self.logger.error(f"查询 {category['name']} 未上传商品失败: {resp}")
            return []
            
        result = resp.get("result", {})
        items = result.get("items", [])
        total = result.get("total", 0)
        
        self.logger.info(f"查询到 {category['name']} 第 {page} 页商品 {len(items)} 个，总计 {total} 个")
        
        return items
        
    def get_upload_signature(self) -> Optional[str]:
        """
        获取上传签名
        """
        self.random_delay()
        
        payload = {"tag": "flash-tag"}
        self.logger.info("获取上传签名")
        
        resp = self.request.post(self.signature_url, payload)
        
        if not resp or not resp.get("success"):
            self.logger.error(f"获取上传签名失败: {resp}")
            return None
            
        signature = resp.get("result")
        self.logger.info("获取上传签名成功")
        return signature
        
    def upload_image(self, image_path: str, signature: str) -> Optional[str]:
        """
        上传图片到服务器
        """
        if not os.path.exists(image_path):
            self.logger.error(f"图片文件不存在: {image_path}")
            return None
            
        self.random_delay()
        
        # 准备multipart/form-data请求
        files = {
            'url_width_height': (None, 'true'),
            'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/jpeg'),
            'upload_sign': (None, signature)
        }
        
        params = {
            'sdk_version': 'js-0.0.40',
            'tag_name': 'flash-tag'
        }
        
        try:
            # 获取合规请求头
            headers = self.request._get_headers()
            
            # 移除content-type，让requests自动设置multipart的content-type
            if 'content-type' in headers:
                del headers['content-type']
                
            self.logger.info(f"上传图片: {os.path.basename(image_path)}")
            
            response = requests.post(
                self.upload_url,
                params=params,
                files=files,
                headers=headers,
                timeout=180
            )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("url"):
                self.logger.error(f"上传图片失败: {result}")
                return None
                
            image_url = result["url"]
            self.logger.info(f"图片上传成功: {image_url}")
            return image_url
            
        except Exception as e:
            self.logger.error(f"上传图片异常: {str(e)}")
            return None
        finally:
            # 确保文件被关闭
            if 'image' in files:
                files['image'][1].close()
                
    def batch_upload_products(self, spu_ids: List[int], image_url: str) -> Dict[str, Any]:
        """
        批量上传商品实拍图
        """
        self.random_delay()
        
        payload = {
            "spu_ids": spu_ids,
            "confirm_type": 4,
            "upload_image_list": [
                {
                    "type": 2,
                    "image": image_url
                }
            ]
        }
        
        self.logger.info(f"批量上传 {len(spu_ids)} 个商品的实拍图")
        self.logger.debug(f"上传参数: {payload}")
        
        resp = self.request.post(self.batch_upload_url, payload)
        
        if not resp or not resp.get("success"):
            self.logger.error(f"批量上传失败: {resp}")
            return {"success": False, "result": resp}
            
        result = resp.get("result", {})
        total = result.get("total", 0)
        total_success = result.get("total_success", 0)
        total_fail = result.get("total_fail", 0)
        
        self.logger.info(f"批量上传结果: 总计 {total}，成功 {total_success}，失败 {total_fail}")
        
        if total_fail > 0:
            self.logger.warning(f"有 {total_fail} 个商品上传失败")
            
        return resp
        
    def process_category(self, category: Dict[str, Any]) -> bool:
        """
        处理单个品类的所有商品，持续处理第一页直到完成
        """
        self.logger.info(f"===== 开始处理品类: {category['name']} =====")

        # 1. 先查询第一页，看是否有商品，如果没有则直接跳过
        if self.stop_flag_callback(): return False
        initial_products = self.get_pending_products(category, page=1)
        if not initial_products:
            self.logger.info(f"品类 {category['name']} 当前没有需要处理的商品，跳过。")
            return True

        # 2. 如果有商品，再获取签名和上传图片
        self.logger.info(f"品类 {category['name']} 发现待处理商品，正在准备上传资源...")
        if self.stop_flag_callback(): return False
        signature = self.get_upload_signature()
        if not signature:
            self.logger.error(f"获取上传签名失败，跳过品类 {category['name']}")
            return False
            
        if self.stop_flag_callback(): return False
        image_path = os.path.join(self.images_dir, category["image_file"])
        if not os.path.exists(image_path):
            self.logger.error(f"图片文件不存在: {image_path}，跳过品类 {category['name']}")
            return False
            
        if self.stop_flag_callback(): return False
        image_url = self.upload_image(image_path, signature)
        if not image_url:
            self.logger.error(f"上传图片失败，跳过品类 {category['name']}")
            return False
            
        total_processed_in_category = 0
        
        # 3. 循环处理第一页，直到第一页返回空
        while True:
            if self.stop_flag_callback():
                self.logger.info(f"检测到停止信号，中断 {category['name']} 的处理。")
                break
                
            # 每次都重新获取第一页的商品
            products = self.get_pending_products(category, page=1)
            if not products:
                self.logger.info(f"品类 {category['name']} 第一页已无待处理商品，该品类处理完成。")
                break
                
            # 提取SPU ID列表
            spu_ids = [product["spu_id"] for product in products]
            
            # 批量上传
            result = self.batch_upload_products(spu_ids, image_url)
            
            if result.get("success"):
                success_count = result.get("result", {}).get("total_success", 0)
                fail_count = result.get("result", {}).get("total_fail", 0)
                total_processed_in_category += success_count
                self.logger.info(f"品类 {category['name']}：处理了一批商品，成功 {success_count} 个，失败 {fail_count} 个。")
            else:
                self.logger.error(f"品类 {category['name']}：处理一批商品时发生API错误。")
            
        self.logger.info(f"品类 {category['name']} 处理结束，共成功处理 {total_processed_in_category} 个商品。")
        return True
        
    def batch_upload_all(self):
        """
        主流程：依次处理所选品类
        """
        total_categories = len(self.categories)
        
        for idx, category in enumerate(self.categories):
            if self.stop_flag_callback():
                self.logger.info("检测到停止信号，中断所有上传任务。")
                break
                
            self.logger.info(f"开始处理第 {idx + 1}/{total_categories} 个品类: {category['name']}")
            
            try:
                success = self.process_category(category)
                if not success:
                    self.logger.error(f"品类 {category['name']} 处理失败，继续下一个品类")
                    
            except Exception as e:
                self.logger.error(f"处理品类 {category['name']} 时发生异常: {str(e)}")
                continue
                
            # 更新总体进度
            if self.progress_callback:
                progress = ((idx + 1) / total_categories) * 100
                self.progress_callback(progress)
                
            # 品类间延迟
            if idx < total_categories - 1:
                if self.stop_flag_callback():
                    self.logger.info("检测到停止信号，不再处理下一个品类。")
                    break
                self.random_delay()
                
        if not self.stop_flag_callback():
            self.logger.info("所有品类处理完成")
        else:
            self.logger.info("上传任务已由用户手动停止。") 