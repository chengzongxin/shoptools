import React, { useEffect, useState } from 'react';
import { Card, Button, Typography } from 'antd';
import { useAuth } from '../../contexts/AuthContext';

const { Title, Text } = Typography;

// 最简单的文件测试组件
const SimpleFileTest: React.FC = () => {
  const { token } = useAuth();
  const [result, setResult] = useState<string>('');

  const testAPI = async () => {
    if (!token) {
      setResult('错误: 没有认证令牌');
      return;
    }

    try {
      console.log('开始测试 API 调用...');
      console.log('Token:', token);
      
      const response = await fetch('/api/files/list', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('响应状态:', response.status);
      console.log('响应头:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('响应数据:', data);
      
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('API 调用失败:', error);
      setResult(`错误: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  useEffect(() => {
    if (token) {
      testAPI();
    }
  }, [token]);

  return (
    <Card title="简单文件 API 测试" style={{ margin: 20 }}>
      <div style={{ marginBottom: 16 }}>
        <Button onClick={testAPI}>
          重新测试
        </Button>
        <Text style={{ marginLeft: 16 }}>
          认证状态: {token ? '已认证' : '未认证'}
        </Text>
      </div>

      <Title level={4}>API 响应结果:</Title>
      <pre style={{ 
        background: '#f5f5f5', 
        padding: 16, 
        borderRadius: 4,
        overflow: 'auto',
        maxHeight: 400
      }}>
        {result || '等待响应...'}
      </pre>
    </Card>
  );
};

export default SimpleFileTest; 