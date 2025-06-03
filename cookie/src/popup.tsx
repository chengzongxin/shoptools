import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

interface Cookie {
  name: string;
  value: string;
  domain: string;
  path: string;
}

interface Header {
  name: string;
  value: string;
}

interface RequestInfo {
  url: string;
  method: string;
  type: string;
  headers: Header[];
  timestamp: string;
}

const Popup: React.FC = () => {
  const [cookies, setCookies] = useState<Cookie[]>([]);
  const [error, setError] = useState<string>('');
  const [count, setCount] = useState<number>(0);
  const [copyStatus, setCopyStatus] = useState<string>('');
  const [requestInfos, setRequestInfos] = useState<{ [key: string]: RequestInfo }>({});
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [filterText, setFilterText] = useState<string>('');

  // 定期刷新请求信息
  useEffect(() => {
    const fetchRequests = () => {
      chrome.runtime.sendMessage({ action: 'getAntiContent' }, (response) => {
        console.log('获取到的请求信息:', response);
        setRequestInfos(response);
        setDebugInfo(`上次刷新时间: ${new Date().toLocaleString()}`);
      });
    };

    // 立即执行一次
    fetchRequests();

    // 每5秒刷新一次
    const interval = setInterval(fetchRequests, 5000);

    return () => clearInterval(interval);
  }, []);

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

  const handleCopyHeader = async (headerValue: string) => {
    try {
      await navigator.clipboard.writeText(headerValue);
      setCopyStatus('复制成功！');
      setTimeout(() => setCopyStatus(''), 2000);
    } catch (err) {
      setCopyStatus('复制失败！');
      console.error('复制失败:', err);
    }
  };

  const handleRefresh = () => {
    chrome.runtime.sendMessage({ action: 'getAntiContent' }, (response) => {
      console.log('手动刷新获取到的请求信息:', response);
      setRequestInfos(response);
      setDebugInfo(`手动刷新时间: ${new Date().toLocaleString()}`);
    });
  };

  // 新增：提取所有请求头的最新值
  const getLatestHeaders = () => {
    // 先按时间倒序排列所有请求
    const allRequests = Object.values(requestInfos)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    const latestHeaders: { [name: string]: { value: string, url: string, timestamp: string } } = {};

    for (const req of allRequests) {
      for (const header of req.headers) {
        // 只保留第一次出现的（即最新的）
        if (!latestHeaders[header.name]) {
          latestHeaders[header.name] = {
            value: header.value,
            url: req.url,
            timestamp: req.timestamp
          };
        }
      }
    }
    return latestHeaders;
  };

  const latestHeaders = getLatestHeaders();

  return (
    <div style={{ width: '600px', padding: '10px', fontFamily: 'Arial, sans-serif' }}>
      <h2>请求头获取器</h2>
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
      
      {/* 请求信息部分 */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>最新请求头（每个字段仅显示一次）</h3>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="搜索请求头..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              style={{
                padding: '4px 8px',
                borderRadius: '4px',
                border: '1px solid #ccc',
                width: '200px'
              }}
            />
            <button
              onClick={handleRefresh}
              style={{
                padding: '4px 8px',
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              刷新
            </button>
          </div>
        </div>
        {debugInfo && (
          <div style={{ 
            fontSize: '12px', 
            color: '#666', 
            marginBottom: '5px' 
          }}>
            {debugInfo}
          </div>
        )}
        <div style={{
          maxHeight: '400px',
          overflowY: 'auto',
          border: '1px solid #ccc',
          padding: '10px',
          marginTop: '10px'
        }}>
          {Object.keys(latestHeaders).length === 0 ? (
            <div style={{ color: '#666', textAlign: 'center' }}>
              暂无请求头信息，请访问目标网站并刷新
            </div>
          ) : (
            Object.entries(latestHeaders)
              .filter(([name, info]) => {
                if (!filterText) return true;
                const searchText = filterText.toLowerCase();
                return (
                  name.toLowerCase().includes(searchText) ||
                  info.value.toLowerCase().includes(searchText) ||
                  info.url.toLowerCase().includes(searchText)
                );
              })
              .map(([name, info]) => (
                <div
                  key={name}
                  style={{
                    marginBottom: '15px',
                    padding: '10px',
                    borderBottom: '1px solid #eee',
                    backgroundColor: '#f8f9fa'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ color: '#2196F3' }}>{name}:</strong>
                    <button
                      onClick={() => handleCopyHeader(info.value)}
                      style={{
                        padding: '2px 6px',
                        backgroundColor: '#2196F3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      复制
                    </button>
                  </div>
                  <div style={{
                    marginTop: '2px',
                    wordBreak: 'break-all',
                    fontSize: '13px'
                  }}>
                    {info.value}
                  </div>
                  <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
                    来源URL: {info.url}<br />
                    时间: {new Date(info.timestamp).toLocaleString()}
                  </div>
                </div>
              ))
          )}
        </div>
      </div>
      
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