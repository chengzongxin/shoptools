import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

interface Cookie {
  name: string;
  value: string;
  domain: string;
  path: string;
}

const Popup: React.FC = () => {
  const [cookies, setCookies] = useState<Cookie[]>([]);
  const [error, setError] = useState<string>('');
  const [count, setCount] = useState<number>(0);
  const [copyStatus, setCopyStatus] = useState<string>('');

  const getCurrentTabUrl = async (): Promise<string> => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab.url || '';
  };

  const getAllCookies = async (url: string): Promise<Cookie[]> => {
    return await chrome.cookies.getAll({ url });
  };

  const handleGetCookies = async () => {
    try {
      const url = await getCurrentTabUrl();
      const cookieList = await getAllCookies(url);
      setCookies(cookieList);
      setError('');
      setCount(prev => prev + 1);
    } catch (err) {
      setError('获取cookie时出错');
      console.error('获取cookie时出错:', err);
    }
  };

  const formatCookies = (cookies: Cookie[]): string => {
    return cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
  };

  const handleCopyCookies = async () => {
    try {
      const cookieString = formatCookies(cookies);
      await navigator.clipboard.writeText(cookieString);
      setCopyStatus('复制成功！');
      setTimeout(() => setCopyStatus(''), 2000);
    } catch (err) {
      setCopyStatus('复制失败！');
      console.error('复制失败:', err);
    }
  };

  return (
    <div style={{ width: '400px', padding: '10px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Cookie获取器</h2>
      <div style={{ marginBottom: '10px' }}>
        已获取次数: {count}
      </div>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
        <button 
          onClick={handleGetCookies}
          style={{
            padding: '8px 16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            flex: 1
          }}
        >
          获取当前页面Cookie
        </button>
        <button 
          onClick={handleCopyCookies}
          disabled={cookies.length === 0}
          style={{
            padding: '8px 16px',
            backgroundColor: cookies.length === 0 ? '#cccccc' : '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: cookies.length === 0 ? 'not-allowed' : 'pointer',
            flex: 1
          }}
        >
          一键复制Cookie
        </button>
      </div>
      {copyStatus && (
        <div style={{ 
          padding: '8px', 
          backgroundColor: copyStatus.includes('成功') ? '#e8f5e9' : '#ffebee',
          color: copyStatus.includes('成功') ? '#2e7d32' : '#c62828',
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          {copyStatus}
        </div>
      )}
      
      <div style={{
        maxHeight: '300px',
        overflowY: 'auto',
        border: '1px solid #ccc',
        padding: '10px',
        marginTop: '10px'
      }}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {cookies.length === 0 && !error && <p>没有找到cookie</p>}
        {cookies.map((cookie, index) => (
          <div 
            key={index}
            style={{
              marginBottom: '10px',
              padding: '5px',
              borderBottom: '1px solid #eee'
            }}
          >
            <strong>{cookie.name}</strong><br />
            值: {cookie.value}<br />
            域名: {cookie.domain}<br />
            路径: {cookie.path}
          </div>
        ))}
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <Popup />
  </React.StrictMode>
); 