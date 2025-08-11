import React from 'react';
import { Button, message } from 'antd';

const SimpleTest: React.FC = () => {
  const handleClick = () => {
    console.log('SimpleTest: 点击按钮');
    message.success('SimpleTest: 消息显示成功！');
  };

  return (
    <div style={{ padding: 20, border: '1px solid #ccc', margin: 10 }}>
      <h4>简单测试组件（官方推荐方式）</h4>
      <Button type="primary" onClick={handleClick}>
        测试消息
      </Button>
    </div>
  );
};

export default SimpleTest; 