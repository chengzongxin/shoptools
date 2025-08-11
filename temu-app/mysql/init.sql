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

-- 创建文件记录表
CREATE TABLE IF NOT EXISTS file_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    stored_name VARCHAR(255) NOT NULL COMMENT '存储文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_size BIGINT NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(100) COMMENT '文件类型',
    uploaded_by VARCHAR(50) NOT NULL COMMENT '上传用户',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    INDEX idx_uploaded_by (uploaded_by),
    INDEX idx_upload_time (upload_time),
    INDEX idx_file_type (file_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件记录表';

-- 创建用户配置表
CREATE TABLE IF NOT EXISTS user_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    seller_cookie TEXT COMMENT '商家中心Cookie',
    compliance_cookie TEXT COMMENT '合规中心Cookie',
    mallid VARCHAR(100) COMMENT 'MallId',
    parent_msg_id VARCHAR(100) COMMENT '父消息ID',
    parent_msg_timestamp VARCHAR(100) COMMENT '父消息时间戳',
    tool_id VARCHAR(100) COMMENT '工具ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_config (user_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户配置表';

-- 插入默认管理员用户（密码：admin123）
-- 使用bcrypt生成的哈希值
INSERT IGNORE INTO users (username, email, password_hash, is_admin) VALUES 
('admin', 'admin@temu-app.com', '$2b$12$PyBp2icYlJs2xasCZOcM3OYktGz7uAEIAOaYNE6EZ3SZjUFKCyfcC', TRUE);

-- 显示创建结果
SELECT 'Database and tables created successfully!' as message; 