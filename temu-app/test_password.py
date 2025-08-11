#!/usr/bin/env python3
"""
密码验证测试脚本
用于测试bcrypt密码加密和验证功能
"""

from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password():
    """测试密码加密和验证"""
    test_password = "admin123"
    
    print("🔐 测试密码加密和验证功能...")
    print(f"测试密码: {test_password}")
    
    # 生成密码哈希
    hashed_password = pwd_context.hash(test_password)
    print(f"密码哈希: {hashed_password}")
    
    # 验证密码
    is_valid = pwd_context.verify(test_password, hashed_password)
    print(f"密码验证结果: {is_valid}")
    
    # 测试错误密码
    wrong_password = "wrong123"
    is_wrong_valid = pwd_context.verify(wrong_password, hashed_password)
    print(f"错误密码验证结果: {is_wrong_valid}")
    
    # 测试数据库中存储的哈希值
    db_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G"
    db_valid = pwd_context.verify(test_password, db_hash)
    print(f"数据库哈希验证结果: {db_valid}")
    
    return db_valid

if __name__ == "__main__":
    try:
        result = test_password()
        if result:
            print("✅ 密码验证功能正常！")
        else:
            print("❌ 密码验证失败！")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        print("请检查bcrypt版本兼容性") 