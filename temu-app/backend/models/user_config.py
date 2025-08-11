from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base

class UserConfig(Base):
    """用户配置模型"""
    __tablename__ = "user_configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    kuajingmaihuo_cookie = Column(Text, comment="跨境猫卖家中心Cookie")
    agentseller_cookie = Column(Text, comment="TEMU代理商中心Cookie")
    mallid = Column(String(100), comment="MallId")
    parent_msg_id = Column(String(100), comment="父消息ID")
    parent_msg_timestamp = Column(String(100), comment="父消息时间戳")
    tool_id = Column(String(100), comment="工具ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<UserConfig(user_id={self.user_id}, mallid='{self.mallid}', kuajingmaihuo_cookie='{self.kuajingmaihuo_cookie}', agentseller_cookie='{self.agentseller_cookie}')>"
