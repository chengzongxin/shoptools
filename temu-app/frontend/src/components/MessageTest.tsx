import React from 'react';
import { Button, message, notification } from 'antd';
import { message as messageApi } from 'antd';

const MessageTest: React.FC = () => {
  const testMessage = () => {
    console.log('Testing message...');
    message.success('这是一个成功的消息！');
  };

  const testMessageApi = () => {
    console.log('Testing message API...');
    messageApi.success('这是API方式的消息！');
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

  return (
    <div style={{ padding: 20 }}>
      <h3>消息测试组件</h3>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <Button type="primary" onClick={testMessage}>
          测试 Message 组件
        </Button>
        <Button type="default" onClick={testMessageApi}>
          测试 Message API
        </Button>
        <Button type="dashed" onClick={testNotification}>
          测试 Notification
        </Button>
        <Button type="text" onClick={testAlert}>
          测试原生 Alert
        </Button>
      </div>
    </div>
  );
};

export default MessageTest; 