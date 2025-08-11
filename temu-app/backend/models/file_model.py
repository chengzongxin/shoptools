from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from database.connection import Base

class FileRecord(Base):
    """文件记录模型"""
    __tablename__ = "file_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    stored_name = Column(String(255), nullable=False, comment="存储文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_type = Column(String(100), nullable=True, comment="文件类型")
    uploaded_by = Column(String(50), nullable=False, comment="上传用户")
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), comment="上传时间")
    
    def __repr__(self):
        return f"<FileRecord(id={self.id}, original_name='{self.original_name}', uploaded_by='{self.uploaded_by}')>" 