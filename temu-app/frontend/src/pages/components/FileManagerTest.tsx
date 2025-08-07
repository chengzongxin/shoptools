import React, { useEffect, useState } from 'react';
import { Card, Button, List, Typography } from 'antd';
import { useAuth } from '../../contexts/AuthContext';
import { getFileList } from '../api';
import type { FileRecord } from '../types/file';

const { Title, Text } = Typography;

// 文件管理测试组件
const FileManagerTest: React.FC = () => {
  const { token } = useAuth();
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    if (!token) {
      setError('未提供认证令牌');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      console.log('测试组件: 开始获取文件列表');
      const response = await getFileList(token);
      console.log('测试组件: 获取到响应:', response);
      
      if (response.success && response.data) {
        setFiles(response.data);
        console.log('测试组件: 设置文件列表:', response.data);
      } else {
        setError('响应格式不正确');
      }
    } catch (err) {
      console.error('测试组件: 获取文件列表失败:', err);
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchFiles();
    }
  }, [token]);

  return (
    <Card title="文件管理测试" style={{ margin: 20 }}>
      <div style={{ marginBottom: 16 }}>
        <Button onClick={fetchFiles} loading={loading}>
          刷新文件列表
        </Button>
        <Text style={{ marginLeft: 16 }}>
          认证状态: {token ? '已认证' : '未认证'}
        </Text>
      </div>

      {error && (
        <div style={{ color: 'red', marginBottom: 16 }}>
          错误: {error}
        </div>
      )}

      <Title level={4}>文件列表 ({files.length} 个文件)</Title>
      
      <List
        dataSource={files}
        loading={loading}
        renderItem={(file) => (
          <List.Item>
            <List.Item.Meta
              title={file.original_name}
              description={
                <div>
                  <Text>大小: {file.file_size} 字节</Text>
                  <br />
                  <Text>类型: {file.file_type}</Text>
                  <br />
                  <Text>上传者: {file.uploaded_by}</Text>
                  <br />
                  <Text>上传时间: {file.upload_time}</Text>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

export default FileManagerTest; 