import React from 'react';
import { App } from 'antd';

interface MessageProviderProps {
  children: React.ReactNode;
}

const MessageProvider: React.FC<MessageProviderProps> = ({ children }) => {
  return (
    <App
      message={{
        top: 60,
        duration: 3,
        maxCount: 3,
      }}
      notification={{
        placement: 'topRight',
        duration: 4.5,
        maxCount: 3,
      }}
    >
      {children}
    </App>
  );
};

export default MessageProvider; 