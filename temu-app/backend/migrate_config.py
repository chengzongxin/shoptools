#!/usr/bin/env python3
"""
配置迁移脚本
将现有的 config.json 文件配置迁移到数据库中的用户配置表
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.connection import engine
from models.user import User
from models.user_config import UserConfig
from sqlalchemy.orm import sessionmaker

def migrate_configs():
    """迁移配置文件到数据库"""
    print("🔄 开始配置迁移...")
    
    # 配置文件路径
    config_path = project_root / "config.json"
    
    if not config_path.exists():
        print("ℹ️  未找到 config.json 文件，无需迁移")
        return
    
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            old_config = json.load(f)
        
        print(f"📁 发现配置文件: {config_path}")
        print(f"📋 配置内容: {list(old_config.keys())}")
        
        # 创建数据库会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 查找管理员用户（假设使用admin用户）
            admin_user = db.query(User).filter(User.username == "admin").first()
            
            if not admin_user:
                print("❌ 未找到admin用户，请先创建用户")
                return
            
            # 检查是否已有配置（使用传统的外键查询）
            existing_config = db.query(UserConfig).filter(UserConfig.user_id == admin_user.id).first()
            
            if existing_config:
                print("ℹ️  admin用户已有配置，跳过迁移")
                return
            
            # 创建新配置（字段名映射）
            new_config = UserConfig(
                user_id=admin_user.id,
                kuajingmaihuo_cookie=old_config.get("seller_cookie"),  # 旧字段映射到新字段
                agentseller_cookie=old_config.get("compliance_cookie"),  # 旧字段映射到新字段
                mallid=old_config.get("mallid"),
                parent_msg_id=old_config.get("parent_msg_id"),
                parent_msg_timestamp=old_config.get("parent_msg_timestamp"),
                tool_id=old_config.get("tool_id")
            )
            
            db.add(new_config)
            db.commit()
            
            print("✅ 配置迁移成功！")
            print(f"👤 用户: {admin_user.username}")
            print(f"🔧 配置项: {list(old_config.keys())}")
            print("📝 字段映射:")
            print("   seller_cookie → kuajingmaihuo_cookie (跨境猫卖家中心)")
            print("   compliance_cookie → agentseller_cookie (TEMU代理商中心)")
            
            # 备份原配置文件
            backup_path = config_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(old_config, f, ensure_ascii=False, indent=2)
            
            print(f"💾 原配置文件已备份到: {backup_path}")
            
            # 询问是否删除原配置文件
            response = input("🗑️  是否删除原配置文件？(y/N): ").strip().lower()
            if response == 'y':
                config_path.unlink()
                print("🗑️  原配置文件已删除")
            else:
                print("ℹ️  原配置文件保留")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False
    
    return True

def create_default_configs():
    """为所有现有用户创建默认配置"""
    print("🔧 为现有用户创建默认配置...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 获取所有没有配置的用户（使用传统的外键查询）
        # 使用子查询找到没有配置的用户
        users_with_config = db.query(UserConfig.user_id).subquery()
        users_without_config = db.query(User).filter(~User.id.in_(users_with_config)).all()
        
        if not users_without_config:
            print("ℹ️  所有用户都有配置，无需创建默认配置")
            return
        
        print(f"👥 发现 {len(users_without_config)} 个用户需要创建配置")
        
        for user in users_without_config:
            # 创建空配置
            new_config = UserConfig(
                user_id=user.id,
                kuajingmaihuo_cookie=None,
                agentseller_cookie=None,
                mallid=None,
                parent_msg_id=None,
                parent_msg_timestamp=None,
                tool_id=None
            )
            
            db.add(new_config)
            print(f"✅ 为用户 {user.username} 创建了默认配置")
        
        db.commit()
        print("🎉 所有默认配置创建完成！")
        
    except Exception as e:
        print(f"❌ 创建默认配置失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 TEMU工具箱配置迁移工具")
    print("=" * 50)
    
    # 执行迁移
    if migrate_configs():
        print("\n" + "=" * 50)
        create_default_configs()
        print("\n🎯 迁移完成！现在每个用户都有独立的配置了。")
    else:
        print("\n❌ 迁移失败，请检查错误信息")
        sys.exit(1)
