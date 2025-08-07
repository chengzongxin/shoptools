import React from 'react';
import { Button, Card, Space, message, notification } from 'antd';
import { useNavigate } from 'react-router-dom';
import SimpleTest from '../components/SimpleTest';

const TestPage: React.FC = () => {
  const navigate = useNavigate();

  const testMessage = () => {
    console.log('Testing message...');
    message.success('这是一个成功的消息！');
  };

  const testNotification = () => {
    console.log('Testing notification...');
    notification.success({
      message: '通知标题',
      description: '这是一个通知消息！',
    });
  };

  const testAlert = () => {
    console.log('Testing alert...');
    alert('这是原生alert消息！');
  };

  const testError = () => {
    console.log('Testing error message...');
    message.error('这是一个错误消息！');
  };

  const testWarning = () => {
    console.log('Testing warning message...');
    message.warning('这是一个警告消息！');
  };

  return (
    <div style={{ padding: 20 }}>
      <Card title="消息测试页面" style={{ maxWidth: 800, margin: '0 auto' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <h3>简单测试组件</h3>
            <SimpleTest />
          </div>

          <div>
            <h3>测试Ant Design消息组件（官方推荐方式）</h3>
            <Space wrap>
              <Button type="primary" onClick={testMessage}>
                测试成功消息
              </Button>
              <Button type="default" onClick={testError}>
                测试错误消息
              </Button>
              <Button type="default" onClick={testWarning}>
                测试警告消息
              </Button>
              <Button type="default" onClick={testNotification}>
                测试通知
              </Button>
              <Button type="dashed" onClick={testAlert}>
                测试原生Alert
              </Button>
            </Space>
          </div>
          
          <div>
            <h3>导航测试</h3>
            <Space>
              <Button onClick={() => navigate('/login')}>
                去登录页面
              </Button>
              <Button onClick={() => navigate('/compliance')}>
                去主页面
              </Button>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default TestPage; 