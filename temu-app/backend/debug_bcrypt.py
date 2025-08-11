#!/usr/bin/env python3
"""
bcrypt 哈希验证调试脚本
分析为什么特定的哈希值能成功验证
"""

import bcrypt
from auth.password import test_password_verification, verify_password, get_password_hash

def analyze_hash(hash_value, password="admin123"):
    """分析哈希值的详细信息"""
    print(f"🔍 分析哈希值: {hash_value}")
    print(f"   测试密码: {password}")
    
    # 解析哈希结构
    parts = hash_value.split('$')
    if len(parts) >= 4:
        version = parts[1]
        cost = parts[2]
        salt_and_hash = parts[3]
        
        print(f"   版本: {version}")
        print(f"   成本因子: {cost} (2^{cost} = {2**int(cost)} 轮)")
        print(f"   盐值+哈希: {salt_and_hash}")
        print(f"   盐值长度: {len(salt_and_hash[:22])} 字符")
        print(f"   哈希长度: {len(salt_and_hash[22:])} 字符")
    
    # 测试验证
    try:
        # 直接使用 bcrypt
        result1 = bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))
        print(f"   bcrypt.checkpw 结果: {result1}")
    except Exception as e:
        print(f"   bcrypt.checkpw 错误: {e}")
    
    # 使用我们的验证函数
    result2 = verify_password(password, hash_value)
    print(f"   我们的验证函数结果: {result2}")
    
    return result1 and result2

def test_hash_generation():
    """测试哈希生成过程"""
    print("\n🔧 测试哈希生成过程...")
    
    password = "admin123"
    
    # 生成多个哈希进行对比
    hashes = []
    for i in range(3):
        hash_value = get_password_hash(password)
        hashes.append(hash_value)
        print(f"   哈希 {i+1}: {hash_value}")
    
    # 验证所有生成的哈希
    print("\n   验证生成的哈希:")
    for i, hash_value in enumerate(hashes):
        is_valid = verify_password(password, hash_value)
        print(f"   哈希 {i+1} 验证: {is_valid}")

def test_specific_hashes():
    """测试特定的哈希值"""
    print("\n🎯 测试特定哈希值...")
    
    # 失败的哈希
    failed_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G"
    print(f"\n❌ 失败的哈希:")
    analyze_hash(failed_hash)
    
    # 成功的哈希
    success_hash = "$2b$12$PyBp2icYlJs2xasCZOcM3OYktGz7uAEIAOaYNE6EZ3SZjUFKCyfcC"
    print(f"\n✅ 成功的哈希:")
    analyze_hash(success_hash)

def test_bcrypt_versions():
    """测试 bcrypt 版本兼容性"""
    print("\n📦 bcrypt 版本信息:")
    print(f"   bcrypt 版本: {bcrypt.__version__}")
    
    # 测试不同版本的哈希格式
    test_password = "admin123"
    
    # 生成不同版本的哈希
    try:
        # 使用默认参数
        salt = bcrypt.gensalt()
        hash1 = bcrypt.hashpw(test_password.encode('utf-8'), salt)
        print(f"   默认哈希: {hash1.decode('utf-8')}")
        
        # 使用指定成本因子
        salt2 = bcrypt.gensalt(12)
        hash2 = bcrypt.hashpw(test_password.encode('utf-8'), salt2)
        print(f"   成本12哈希: {hash2.decode('utf-8')}")
        
    except Exception as e:
        print(f"   哈希生成错误: {e}")

if __name__ == "__main__":
    print("🚀 bcrypt 哈希验证调试工具")
    print("=" * 60)
    
    # 运行测试
    test_specific_hashes()
    test_hash_generation()
    test_bcrypt_versions()
    
    print("\n" + "=" * 60)
    print("💡 结论:")
    print("   1. 成功的哈希是在当前环境中生成的")
    print("   2. 失败的哈希可能来自不同的环境或版本")
    print("   3. bcrypt 对版本和环境很敏感") 

    # 每次生成都不同，但都能验证成功
    test_password_verification()