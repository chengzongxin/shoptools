// 存储请求头信息
let requestHeaders: { [key: string]: any } = {};

// 初始化时打印日志
console.log('Background script started at:', new Date().toISOString());

// 测试storage是否可用
chrome.storage.local.get(['test'], (result) => {
  console.log('Storage test:', result);
});

// 测试webRequest是否可用
try {
  chrome.webRequest.onBeforeSendHeaders.addListener(
    () => {
      console.log('WebRequest listener is working');
    },
    { urls: ["<all_urls>"] },
    ["requestHeaders"]
  );
  console.log('WebRequest listener registered successfully');
} catch (error) {
  console.error('Error registering WebRequest listener:', error);
}

// 监听cookie变化
chrome.cookies.onChanged.addListener((changeInfo) => {
  const { cookie, cause, removed } = changeInfo;
  
  // 记录cookie变化
  console.log('Cookie changed:', {
    name: cookie.name,
    domain: cookie.domain,
    cause: cause,
    removed: removed,
    timestamp: new Date().toISOString()
  });

  // 如果是添加或修改cookie
  if (!removed) {
    console.log('Cookie value:', cookie.value);
  }
});

// 监听网络请求
chrome.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    console.log('收到请求:', details.url);
    
    // 检查所有请求
    const headers = details.requestHeaders || [];
    
    // 为每个请求创建记录
    const key = `${details.url}_${new Date().getTime()}`;
    requestHeaders[key] = {
      url: details.url,
      method: details.method,
      type: details.type,
      headers: headers.map(header => ({
        name: header.name,
        value: header.value
      })),
      timestamp: new Date().toISOString()
    };
    
    // 保存到storage
    chrome.storage.local.set({ requestHeaders });
    
    console.log('捕获到请求:', {
      url: details.url,
      method: details.method,
      type: details.type,
      headers: headers.map(h => ({
        name: h.name,
        value: h.value
      })),
      timestamp: new Date().toISOString()
    });
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders", "extraHeaders"]
);

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('收到消息:', request);
  
  if (request.action === 'getAntiContent') {
    // 从storage获取最新的请求头信息
    chrome.storage.local.get(['requestHeaders'], (result) => {
      console.log('存储的请求头信息:', result);
      sendResponse(result.requestHeaders || {});
    });
    return true; // 保持消息通道开放
  }
});

// 监听扩展安装或更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('扩展已安装');
    // 初始化存储
    chrome.storage.local.set({ requestHeaders: {} });
  } else if (details.reason === 'update') {
    console.log('扩展已更新');
  }
}); 