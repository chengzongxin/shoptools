import requests
import json
import time
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union, Any

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class IllegalDetail:
    """违规详情"""
    title: Optional[str]
    value: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IllegalDetail':
        """从字典创建对象"""
        return cls(
            title=data.get('title'),
            value=data.get('value', '')
        )

@dataclass
class PunishDetail:
    """处罚详情"""
    punish_id: int
    target_id: Optional[int]
    target_type: Optional[str]
    violation_type: int
    punish_infect_desc: str
    site_id: int
    remarks: Optional[str]
    status: int
    now_appeal_time: int
    max_appeal_time: int
    start_time: int
    plan_end_time: int
    real_end_time: Optional[int]
    appeal_id: Optional[int]
    appeal_status: int
    appeal_create_time: Optional[int]
    appeal_end_time: Optional[int]
    appeal_over_due: bool
    punish_appeal_type: Optional[str]
    illegal_detail: List[IllegalDetail]
    rectification_suggestion: str
    create_from_upgrade: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PunishDetail':
        """从字典创建对象"""
        try:
            if not data or not isinstance(data, dict):
                logger.error("无效的处罚详情数据")
                return None
                
            # 处理可能为空的字段
            illegal_details = []
            if 'illegal_detail' in data and isinstance(data['illegal_detail'], list):
                for illegal in data['illegal_detail']:
                    try:
                        if isinstance(illegal, dict):
                            illegal_detail = IllegalDetail.from_dict(illegal)
                            if illegal_detail:
                                illegal_details.append(illegal_detail)
                    except Exception as e:
                        logger.error(f"处理违规详情时出错: {str(e)}")
                        continue
            
            return cls(
                punish_id=data.get('punish_id', 0),
                target_id=data.get('target_id'),
                target_type=data.get('target_type'),
                violation_type=data.get('violation_type', 0),
                punish_infect_desc=data.get('punish_infect_desc', ''),
                site_id=data.get('site_id', 0),
                remarks=data.get('remarks'),
                status=data.get('status', 0),
                now_appeal_time=data.get('now_appeal_time', 0),
                max_appeal_time=data.get('max_appeal_time', 0),
                start_time=data.get('start_time', 0),
                plan_end_time=data.get('plan_end_time', 0),
                real_end_time=data.get('real_end_time'),
                appeal_id=data.get('appeal_id'),
                appeal_status=data.get('appeal_status', 0),
                appeal_create_time=data.get('appeal_create_time'),
                appeal_end_time=data.get('appeal_end_time'),
                appeal_over_due=data.get('appeal_over_due', False),
                punish_appeal_type=data.get('punish_appeal_type'),
                illegal_detail=illegal_details,
                rectification_suggestion=data.get('rectification_suggestion', ''),
                create_from_upgrade=data.get('create_from_upgrade', False)
            )
        except Exception as e:
            logger.error(f"创建PunishDetail对象时出错: {str(e)}")
            logger.error(f"数据: {json.dumps(data, ensure_ascii=False)}")
            return None

@dataclass
class ViolationProduct:
    """违规商品数据类"""
    target_type: str
    target_id: int
    product_mapping_id: int
    goods_id: int
    spu_id: int
    goods_name: str
    goods_img_url: str
    mall_id: int
    mall_name: Optional[str]
    source_punish_name: str
    punish_type: int
    leaf_reason_id: int
    leaf_reason_name: str
    violation_desc: str
    violation_type: int
    site_num: int
    punish_num: int
    punish_detail_list: List[PunishDetail]
    can_appeal_punish_detail_list: List[PunishDetail]
    can_not_appeal: Optional[bool]
    reject_desc: Optional[str]
    appeal_status: int
    misuse_ban_appeal: bool
    appeal_over_due: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationProduct':
        """从字典创建对象"""
        try:
            if not data or not isinstance(data, dict):
                logger.error("无效的商品数据")
                return None
                
            # 检查必要字段
            required_fields = ['goods_id', 'goods_name', 'spu_id']
            for field in required_fields:
                if field not in data:
                    logger.error(f"商品数据缺少必要字段: {field}")
                    return None
            
            # 处理可能为空的字段
            punish_detail_list = []
            if 'punish_detail_list' in data and isinstance(data['punish_detail_list'], list):
                for detail in data['punish_detail_list']:
                    try:
                        punish_detail = PunishDetail.from_dict(detail)
                        if punish_detail:
                            punish_detail_list.append(punish_detail)
                    except Exception as e:
                        logger.error(f"处理处罚详情时出错: {str(e)}")
                        continue
            
            can_appeal_list = []
            if 'can_appeal_punish_detail_list' in data and isinstance(data['can_appeal_punish_detail_list'], list):
                for detail in data['can_appeal_punish_detail_list']:
                    try:
                        appeal_detail = PunishDetail.from_dict(detail)
                        if appeal_detail:
                            can_appeal_list.append(appeal_detail)
                    except Exception as e:
                        logger.error(f"处理可申诉详情时出错: {str(e)}")
                        continue
            
            return cls(
                target_type=data.get('target_type', ''),
                target_id=data.get('target_id', 0),
                product_mapping_id=data.get('product_mapping_id', 0),
                goods_id=data.get('goods_id', 0),
                spu_id=data.get('spu_id', 0),
                goods_name=data.get('goods_name', ''),
                goods_img_url=data.get('goods_img_url', ''),
                mall_id=data.get('mall_id', 0),
                mall_name=data.get('mall_name'),
                source_punish_name=data.get('source_punish_name', ''),
                punish_type=data.get('punish_type', 0),
                leaf_reason_id=data.get('leaf_reason_id', 0),
                leaf_reason_name=data.get('leaf_reason_name', ''),
                violation_desc=data.get('violation_desc', ''),
                violation_type=data.get('violation_type', 0),
                site_num=data.get('site_num', 0),
                punish_num=data.get('punish_num', 0),
                punish_detail_list=punish_detail_list,
                can_appeal_punish_detail_list=can_appeal_list,
                can_not_appeal=data.get('can_not_appeal'),
                reject_desc=data.get('reject_desc'),
                appeal_status=data.get('appeal_status', 0),
                misuse_ban_appeal=data.get('misuse_ban_appeal', False),
                appeal_over_due=data.get('appeal_over_due', False)
            )
        except Exception as e:
            logger.error(f"创建ViolationProduct对象时出错: {str(e)}")
            logger.error(f"数据: {json.dumps(data, ensure_ascii=False)}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        try:
            return asdict(self)
        except Exception as e:
            logger.error(f"转换ViolationProduct对象为字典时出错: {str(e)}")
            raise

@dataclass
class ViolationListResult:
    """违规列表结果数据类"""
    punish_appeal_entrance_list: List[ViolationProduct]
    total: int
    error_tips: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationListResult':
        """从字典创建对象"""
        try:
            return cls(
                punish_appeal_entrance_list=[
                    ViolationProduct.from_dict(item)
                    for item in data.get('punish_appeal_entrance_list', [])
                ],
                total=data.get('total', 0),
                error_tips=data.get('error_tips')
            )
        except Exception as e:
            logger.error(f"创建ViolationListResult对象时出错: {str(e)}")
            logger.error(f"数据: {json.dumps(data, ensure_ascii=False)}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        try:
            return asdict(self)
        except Exception as e:
            logger.error(f"转换ViolationListResult对象为字典时出错: {str(e)}")
            raise

@dataclass
class ViolationListResponse:
    """违规列表响应数据类"""
    success: bool
    error_code: int
    error_msg: Optional[str]
    result: ViolationListResult

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationListResponse':
        """从字典创建对象"""
        try:
            return cls(
                success=data.get('success', False),
                error_code=data.get('error_code', 0),
                error_msg=data.get('error_msg'),
                result=ViolationListResult.from_dict(data.get('result', {}))
            )
        except Exception as e:
            logger.error(f"创建ViolationListResponse对象时出错: {str(e)}")
            logger.error(f"数据: {json.dumps(data, ensure_ascii=False)}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        try:
            return asdict(self)
        except Exception as e:
            logger.error(f"转换ViolationListResponse对象为字典时出错: {str(e)}")
            raise

class ViolationListCrawler:
    def __init__(self):
        # 基础URL
        self.base_url = "https://agentseller.temu.com"
        self.api_url = f"{self.base_url}/mms/tmod_punish/agent/merchant_appeal/entrance/list"
        
        # 请求头
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "anti-content": "",
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "cookie": "",
            "mallid": "",
            "origin": "https://agentseller.temu.com",
            "referer": "https://agentseller.temu.com/mms/tmod_punish/agent/merchant_appeal/entrance/list",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
        }
        
        # 分页参数
        self.page_size = 100
        self.current_page = 1
        
    def get_page_data(self, page: int) -> Optional[ViolationListResponse]:
        """获取指定页码的数据"""
        payload = {
            "page_num": page,
            "page_size": self.page_size,
            "target_type": "goods"
        }
        
        try:
            logger.info(f"正在获取第 {page} 页数据")
            logger.debug(f"请求URL: {self.api_url}")
            logger.debug(f"请求头: {json.dumps(self.headers, ensure_ascii=False)}")
            logger.debug(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            # 验证请求头
            if not self.headers.get("cookie"):
                logger.error("Cookie未设置")
                return None
            if not self.headers.get("anti-content"):
                logger.error("Anti-Content未设置")
                return None
            if not self.headers.get("mallid"):
                logger.error("MallID未设置")
                return None
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # 添加超时设置
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                return None
                
            result = response.json()
            
            # 检查响应结构
            if not result.get('success'):
                logger.error(f"API返回错误: {result.get('error_msg')}")
                return None
                
            if 'result' not in result:
                logger.error(f"响应数据格式错误，缺少result字段: {result}")
                return None
                
            if 'punish_appeal_entrance_list' not in result['result']:
                logger.error(f"响应数据格式错误，缺少punish_appeal_entrance_list字段: {result['result']}")
                return None
                
            # 打印获取到的数据数量
            items = result['result']['punish_appeal_entrance_list']
            logger.info(f"获取到 {len(items)} 条数据")
            
            # 打印第一条数据作为示例
            if items:
                logger.info(f"数据示例: {json.dumps(items[0], ensure_ascii=False)}")
            else:
                logger.warning("当前页面没有数据")
                # 检查是否有错误信息
                if 'error_msg' in result:
                    logger.error(f"API返回错误信息: {result['error_msg']}")
                if 'error_code' in result:
                    logger.error(f"API返回错误代码: {result['error_code']}")
            
            # 将响应数据转换为ViolationListResponse对象
            return ViolationListResponse.from_dict(result)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            logger.error(f"响应内容: {response.text}")
            return None
        except Exception as e:
            logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
            return None
            
    def get_all_data(self, start_page: int = 1, max_pages: int = 2) -> List[Dict[str, Any]]:
        """获取指定页数的数据
        
        Args:
            start_page (int): 起始页码
            max_pages (int): 最大页数
            
        Returns:
            List[Dict[str, Any]]: 违规商品数据列表，每个商品数据为字典格式
        """
        all_data = []
        
        for page in range(start_page, start_page + max_pages):
            try:
                result = self.get_page_data(page)
                
                if not result:
                    logger.error(f"第 {page} 页数据获取失败")
                    break
                    
                # 获取违规商品列表数据
                items = result.result.punish_appeal_entrance_list
                if not items:
                    logger.info("没有更多数据")
                    break
                    
                # 将数据类对象转换为字典
                for item in items:
                    try:
                        item_dict = item.to_dict()
                        all_data.append(item_dict)
                    except Exception as e:
                        logger.error(f"转换商品数据为字典时出错: {str(e)}")
                        continue
                
                logger.info(f"已获取第 {page} 页数据，当前共 {len(all_data)} 条记录")
                
                # 检查是否还有更多数据
                if len(all_data) >= result.result.total:
                    logger.info(f"已获取所有数据，共 {result.result.total} 条")
                    break
                
                time.sleep(1)  # 添加延迟，避免请求过快
                
            except Exception as e:
                logger.error(f"处理第 {page} 页数据时发生错误: {str(e)}")
                continue
            
        return all_data 