import logging
import time
import random
from typing import List, Dict, Any, Optional
from ..network.request import NetworkRequest

class ComplianceUploader:
    """
    合规信息批量上传核心逻辑
    """
    def __init__(self, logger: logging.Logger, progress_callback=None):
        self.logger = logger
        self.progress_callback = progress_callback
        self.request = NetworkRequest()
        self.base_url = "https://agentseller.temu.com/ms/bg-flux-ms/compliance_property"
        self.task_types = [
            {"name": "加利福尼亚州65号法案", "task_type": 4},
            {"name": "欧盟负责人", "task_type": 25},
            {"name": "制造商信息", "task_type": 60},
            {"name": "土耳其负责人", "task_type": 84},
        ]
        self.template_cache = {}

    def random_delay(self, min_sec=1, max_sec=2):
        delay = random.uniform(min_sec, max_sec)
        self.logger.info(f"请求前随机延时 {delay:.2f} 秒")
        time.sleep(delay)

    def get_pending_products(self, task_type: int) -> List[Dict[str, Any]]:
        """
        获取未上传指定合规类型的商品列表（只查第一页）
        """
        self.random_delay()
        url = f"{self.base_url}/page_query"
        data = {
            "page_num": 1,
            "page_size": 100,
            "type": 2,
            "task_status_list": [2, 5, 11],
            "query_type": 2,
            "task_type_list": [task_type]
        }
        self.logger.info(f"请求未上传商品列表，task_type={task_type}，请求体: {data}")
        resp = self.request.post(url, data)
        # self.logger.info(f"未上传商品接口返回: {resp}")
        if not resp or not resp.get("success"):
            self.logger.error(f"获取未上传商品失败: {resp}")
            return []
        return resp.get("result", {}).get("data", [])

    def get_template(self, task_type: int) -> Optional[Dict[str, Any]]:
        """
        获取指定合规类型的模板（只获取一次，缓存）
        """
        if task_type in self.template_cache:
            self.logger.info(f"模板已缓存，直接复用，task_type={task_type}")
            return self.template_cache[task_type]
        self.random_delay()
        url = f"{self.base_url}/query_template"
        data = {"similar_batch_operate": True, "wait_task_list": [{"task_type": task_type}]}
        self.logger.info(f"请求模板，task_type={task_type}，请求体: {data}")
        resp = self.request.post(url, data)
        # self.logger.info(f"模板接口返回: {resp}")
        if not resp or not resp.get("success"):
            # self.logger.error(f"获取合规模板失败: {resp}")
            return None
        template_list = resp.get("result", {}).get("template_list", [])
        if not template_list:
            # self.logger.error(f"未获取到合规模板: {resp}")
            return None
        self.template_cache[task_type] = template_list[0]
        # self.logger.info(f"获取到模板内容: {template_list[0]}")
        return template_list[0]

    def upload_compliance(self, task_type: int, products: List[Dict[str, Any]], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量上传合规信息
        """
        self.random_delay()
        url = f"{self.base_url}/batch_edit_compliance"
        good_info_list = []
        for p in products:
            # 找到该商品对应的task_id
            task_id = None
            for t in p.get("wait_task_dtolist", []):
                if t.get("task_type") == task_type:
                    task_id = t.get("task_id")
                    break
            if not task_id:
                continue
            good_info_list.append({
                "spu_id": p["spu_id"],
                "goods_id": p["goods_id"],
                "cat_id": p["cat_id"],
                "task_id": task_id
            })
        self.logger.info(f"本次上传商品数: {len(good_info_list)}")
        if not good_info_list:
            self.logger.info("无可上传商品")
            return {"success": True, "result": {}}
        # 构造上传参数
        if task_type == 4:
            # 加利福尼亚州65号法案
            prop = template["template_property_dtolist"][0]
            property_id = str(prop["property_id"])
            # 查找vid为1000100066（无需警告）
            vid = None
            for v in prop["property_value_list"]:
                if v["vid"] == 1000100066:
                    vid = v["vid"]
                    break
            if vid is None:
                error_msg = "加利福尼亚州65号法案模板未找到vid=1000100066（无需警告），请检查模板配置！"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            template_edit_request = {
                "properties": {property_id: [vid]},
                "images": {},
                "input_text": {},
                "task_type": 4,
                "template_id": template["template_id"]
            }
        else:
            # 其他三种
            template_edit_request = {
                "properties": {},
                "input_text": {},
                "task_type": task_type,
                "rep_detail_list": template.get("rep_detail_list", [])
            }
        data = {
            "good_info_list": good_info_list,
            "template_edit_request": template_edit_request
        }
        resp = self.request.post(url, data)
        if not resp or not resp.get("success"):
            self.logger.error(f"上传合规信息失败: {resp}")
        else:
            self.logger.info(f"上传成功: {resp.get('result', {})}")
            fail_goods = resp.get('result', {}).get('fail_goods_list', [])
            if fail_goods:
                self.logger.error(f"失败商品详情: {fail_goods}")
        return resp

    def batch_upload_all(self):
        """
        主流程：依次处理4种合规类型，循环获取未上传商品并上传，直到全部完成
        """
        total_types = len(self.task_types)
        for idx, t in enumerate(self.task_types):
            self.logger.info(f"开始上传：{t['name']}")
            template = self.get_template(t["task_type"])
            if not template:
                self.logger.error(f"未获取到模板，跳过 {t['name']}")
                continue
            while True:
                products = self.get_pending_products(t["task_type"])
                if not products:
                    self.logger.info(f"{t['name']} 已全部上传完成")
                    break
                self.upload_compliance(t["task_type"], products, template)
                if self.progress_callback:
                    self.progress_callback(((idx + 1) / total_types) * 100) 