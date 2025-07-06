"""
数据模型定义
使用Pydantic定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ViolationStatus(str, Enum):
    """违规记录状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OperationType(str, Enum):
    """操作类型枚举"""
    OFF_SHELF = "off_shelf"
    DELETE_IMAGE = "delete_image"

class OperationStatus(str, Enum):
    """操作状态枚举"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class SearchType(str, Enum):
    """搜索类型枚举"""
    TEMU = "temu"
    BLUE = "blue"

# 基础模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None

# 违规记录相关模型
class ViolationRecord(BaseModel):
    """违规记录模型"""
    id: Optional[int] = None
    spuid: str = Field(..., description="商品SPUID")
    product_name: str = Field(..., description="商品名称")
    violation_type: Optional[str] = Field(None, description="违规类型")
    violation_date: Optional[str] = Field(None, description="违规日期")
    status: ViolationStatus = Field(ViolationStatus.PENDING, description="处理状态")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ViolationCreate(BaseModel):
    """创建违规记录请求模型"""
    spuid: str = Field(..., description="商品SPUID")
    product_name: str = Field(..., description="商品名称")
    violation_type: Optional[str] = Field(None, description="违规类型")
    violation_date: Optional[str] = Field(None, description="违规日期")

class ViolationUpdate(BaseModel):
    """更新违规记录请求模型"""
    status: Optional[ViolationStatus] = None
    violation_type: Optional[str] = None
    violation_date: Optional[str] = None

class ViolationListResponse(BaseResponse):
    """违规记录列表响应"""
    data: List[ViolationRecord]
    total: int
    page: int
    page_size: int

# 搜索相关模型
class SearchRequest(BaseModel):
    """搜索请求模型"""
    keyword: str = Field(..., description="搜索关键词")
    search_type: SearchType = Field(..., description="搜索类型")
    limit: Optional[int] = Field(20, description="结果数量限制")

class TemuProduct(BaseModel):
    """TEMU商品模型"""
    id: str = Field(..., description="商品ID")
    title: str = Field(..., description="商品标题")
    price: Optional[str] = Field(None, description="商品价格")
    image_url: Optional[str] = Field(None, description="商品图片")
    spuid: Optional[str] = Field(None, description="商品SPUID")
    status: Optional[str] = Field(None, description="商品状态")

class BlueImage(BaseModel):
    """图库图片模型"""
    id: str = Field(..., description="图片ID")
    title: str = Field(..., description="图片标题")
    image_url: str = Field(..., description="图片URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    file_size: Optional[str] = Field(None, description="文件大小")
    upload_date: Optional[str] = Field(None, description="上传日期")

class SearchResult(BaseModel):
    """搜索结果模型"""
    keyword: str
    search_type: SearchType
    results: List[Dict[str, Any]]
    total_count: int
    search_time: datetime

class SearchResponse(BaseResponse):
    """搜索响应模型"""
    data: SearchResult

# 操作相关模型
class OperationRequest(BaseModel):
    """操作请求模型"""
    operation_type: OperationType = Field(..., description="操作类型")
    target_ids: List[str] = Field(..., description="目标ID列表")
    target_names: Optional[List[str]] = Field(None, description="目标名称列表")

class OperationRecord(BaseModel):
    """操作记录模型"""
    id: Optional[int] = None
    operation_type: OperationType
    target_id: str
    target_name: Optional[str] = None
    status: OperationStatus = Field(OperationStatus.PENDING, description="操作状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    operation_date: Optional[datetime] = None

class OperationResponse(BaseResponse):
    """操作响应模型"""
    data: List[OperationRecord]

class OperationListResponse(BaseResponse):
    """操作记录列表响应"""
    data: List[OperationRecord]
    total: int

# 批量操作模型
class BatchOperationRequest(BaseModel):
    """批量操作请求模型"""
    violations: List[str] = Field(..., description="违规记录ID列表")
    operations: List[OperationRequest] = Field(..., description="操作列表")

class BatchOperationResponse(BaseResponse):
    """批量操作响应模型"""
    data: Dict[str, Any] = Field(..., description="批量操作结果")

# 配置相关模型
class ConfigItem(BaseModel):
    """配置项模型"""
    key: str = Field(..., description="配置键")
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    updated_at: Optional[datetime] = None

class ConfigUpdate(BaseModel):
    """配置更新请求模型"""
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")

# 统计相关模型
class Statistics(BaseModel):
    """统计数据模型"""
    total_violations: int = Field(0, description="总违规记录数")
    pending_violations: int = Field(0, description="待处理违规记录数")
    completed_violations: int = Field(0, description="已完成违规记录数")
    total_operations: int = Field(0, description="总操作数")
    success_operations: int = Field(0, description="成功操作数")
    failed_operations: int = Field(0, description="失败操作数")
    today_operations: int = Field(0, description="今日操作数")

class StatisticsResponse(BaseResponse):
    """统计响应模型"""
    data: Statistics 