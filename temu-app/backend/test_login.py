from backend.auth.password import get_password_hash, verify_password


def test_login_password():
    """
    测试登录密码，从数据库查询密码并进行验证。

    步骤说明：
    1. 从数据库中查找用户名为 'admin' 的用户的密码哈希。
    2. 如果用户不存在，抛出异常。
    3. 打印查询到的密码哈希。
    4. 使用 verify_password 函数验证明文密码与哈希是否匹配。
    """

    # 导入所需模块
    from database.connection import get_db  # 数据库会话获取函数
    from models import user                 # 用户模型
    from sqlalchemy import select           # SQLAlchemy 查询构造
    from auth.password import verify_password  # 密码验证函数
    from fastapi import HTTPException       # HTTP异常

    # 这里我们假设要验证的明文密码为 'admin123'
    plain_password = "admin123"

    # 使用数据库会话查询
    # get_db() 是一个生成器，不支持 with 语法
    db_gen = get_db()  # 获取生成器对象
    db = next(db_gen)  # 获取数据库会话实例
    try:
        # 查询用户名为 'admin' 的用户的密码哈希
        result = db.execute(
            select(user.User.password_hash).where(user.User.username == "admin")
        )
        user_password_hash = result.scalar_one_or_none()

        # 检查用户是否存在
        if not user_password_hash:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        print(f"查询到的用户密码哈希: {user_password_hash}")

        # 验证明文密码与哈希是否匹配
        is_valid = verify_password(plain_password, user_password_hash)
        if is_valid:
            print("✓ 密码验证通过")
        else:
            print("✗ 密码验证失败")
    finally:
        # 关闭数据库会话，防止资源泄漏
        try:
            db_gen.close()
        except Exception as e:
            print(f"关闭数据库会话时出错: {e}")


def test_password_verification():
    """测试密码验证功能"""
    test_password = "admin123"
    test_hash = get_password_hash(test_password)
    
    print(f"测试密码: {test_password}")
    print(f"生成哈希: {test_hash}")
    print(f"验证结果: {verify_password(test_password, test_hash)}")
    
    return verify_password(test_password, test_hash) 

# main 函数入口
if __name__ == "__main__":
    # test_password_verification()
    test_login_password()
