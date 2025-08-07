-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS temu_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE temu_app;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_admin BOOLEAN DEFAULT FALSE COMMENT '是否管理员',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入默认管理员用户（密码：admin123）
-- 使用bcrypt生成的哈希值
INSERT IGNORE INTO users (username, email, password_hash, is_admin) VALUES 
('admin', 'admin@temu-app.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G', TRUE);

-- 显示创建结果
SELECT 'Database and tables created successfully!' as message; 