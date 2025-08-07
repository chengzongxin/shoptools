from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from database.connection import get_db
from models.file_model import FileRecord
from auth.jwt_handler import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# 文件存储目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 获取当前用户（简化版，实际项目中应该从数据库获取）
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
    return username

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件"""
    try:
        # 检查文件大小
        max_file_size = int(os.getenv("MAX_FILE_SIZE", "4294967296"))  # 默认4GB
        
        # 读取文件内容并检查大小
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"文件大小超过限制，最大允许 {max_file_size / (1024**3):.1f}GB"
            )
        
        # 生成唯一文件名
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # 保存文件记录到数据库
        file_record = FileRecord(
            original_name=file.filename,
            stored_name=unique_filename,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            file_type=file.content_type,
            uploaded_by=current_user,
            upload_time=datetime.now()
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        return {
            "success": True,
            "message": "文件上传成功",
            "data": {
                "id": file_record.id,
                "original_name": file_record.original_name,
                "file_size": file_record.file_size,
                "file_type": file_record.file_type,
                "upload_time": file_record.upload_time.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/list")
async def list_files(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文件列表"""
    try:
        files = db.query(FileRecord).order_by(FileRecord.upload_time.desc()).all()
        
        file_list = []
        for file in files:
            file_list.append({
                "id": file.id,
                "original_name": file.original_name,
                "file_size": file.file_size,
                "file_type": file.file_type,
                "uploaded_by": file.uploaded_by,
                "upload_time": file.upload_time.isoformat(),
                "download_url": f"/api/files/download/{file.id}"
            })
        
        return {
            "success": True,
            "data": file_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载文件"""
    try:
        file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            filename=file_record.original_name,
            media_type=file_record.file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")

@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文件"""
    try:
        file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 删除物理文件
        file_path = Path(file_record.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # 删除数据库记录
        db.delete(file_record)
        db.commit()
        
        return {
            "success": True,
            "message": "文件删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

@router.get("/info/{file_id}")
async def get_file_info(
    file_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文件信息"""
    try:
        file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return {
            "success": True,
            "data": {
                "id": file_record.id,
                "original_name": file_record.original_name,
                "file_size": file_record.file_size,
                "file_type": file_record.file_type,
                "uploaded_by": file_record.uploaded_by,
                "upload_time": file_record.upload_time.isoformat(),
                "download_url": f"/api/files/download/{file_record.id}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}") 