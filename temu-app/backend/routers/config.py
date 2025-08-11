from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from database.connection import get_db
from models.user import User
from models.user_config import UserConfig
from routers.auth import get_current_user

router = APIRouter()

@router.post("/config")
def set_config(
    kuajingmaihuo_cookie: str = Body(...),
    agentseller_cookie: str = Body(...),
    mallid: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置用户配置"""
    try:
        # 查找现有配置
        existing_config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        if existing_config:
            # 检查配置是否有变化
            config_changed = (
                existing_config.kuajingmaihuo_cookie != kuajingmaihuo_cookie or
                existing_config.agentseller_cookie != agentseller_cookie or
                existing_config.mallid != mallid
            )
            
            # 更新配置
            existing_config.kuajingmaihuo_cookie = kuajingmaihuo_cookie
            existing_config.agentseller_cookie = agentseller_cookie
            existing_config.mallid = mallid
            
            # 如果配置有变化，清除缓存数据
            if config_changed:
                existing_config.parent_msg_id = None
                existing_config.parent_msg_timestamp = None
                existing_config.tool_id = None
            
            db.commit()
            db.refresh(existing_config)
            
            return {
                "success": True, 
                "msg": "配置已更新",
                "config_changed": config_changed
            }
        else:
            # 创建新配置
            new_config = UserConfig(
                user_id=current_user.id,
                kuajingmaihuo_cookie=kuajingmaihuo_cookie,
                agentseller_cookie=agentseller_cookie,
                mallid=mallid,
                parent_msg_id=None,
                parent_msg_timestamp=None,
                tool_id=None
            )
            
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            
            return {
                "success": True, 
                "msg": "配置已创建",
                "config_changed": True
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@router.get("/config")
def get_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户配置"""
    try:
        config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        if not config:
            return {"success": False, "msg": "未配置"}
        
        return {
            "success": True, 
            "data": {
                "kuajingmaihuo_cookie": config.kuajingmaihuo_cookie,
                "agentseller_cookie": config.agentseller_cookie,
                "mallid": config.mallid,
                "parent_msg_id": config.parent_msg_id,
                "parent_msg_timestamp": config.parent_msg_timestamp,
                "tool_id": config.tool_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/config/cache")
def update_cache(
    parent_msg_id: Optional[str] = Body(None),
    parent_msg_timestamp: Optional[str] = Body(None),
    tool_id: Optional[str] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户缓存数据"""
    try:
        config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="用户配置不存在")
        
        # 只更新提供的字段
        if parent_msg_id is not None:
            config.parent_msg_id = parent_msg_id
        if parent_msg_timestamp is not None:
            config.parent_msg_timestamp = parent_msg_timestamp
        if tool_id is not None:
            config.tool_id = tool_id
        
        db.commit()
        db.refresh(config)
        
        return {"success": True, "msg": "缓存已更新"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新缓存失败: {str(e)}")

@router.delete("/config")
def clear_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清除用户配置"""
    try:
        config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        if config:
            db.delete(config)
            db.commit()
            return {"success": True, "msg": "配置已清除"}
        else:
            return {"success": True, "msg": "配置不存在"}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清除配置失败: {str(e)}")

@router.get("/config/status")
def get_config_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户配置状态"""
    try:
        config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        if not config:
            return {
                "success": True,
                "data": {
                    "has_config": False,
                    "config_complete": False,
                    "missing_fields": ["kuajingmaihuo_cookie", "agentseller_cookie", "mallid"]
                }
            }
        
        # 检查配置完整性
        missing_fields = []
        if not config.kuajingmaihuo_cookie:
            missing_fields.append("kuajingmaihuo_cookie")
        if not config.agentseller_cookie:
            missing_fields.append("agentseller_cookie")
        if not config.mallid:
            missing_fields.append("mallid")
        
        config_complete = len(missing_fields) == 0
        
        return {
            "success": True,
            "data": {
                "has_config": True,
                "config_complete": config_complete,
                "missing_fields": missing_fields,
                "last_updated": config.updated_at.isoformat() if config.updated_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置状态失败: {str(e)}") 