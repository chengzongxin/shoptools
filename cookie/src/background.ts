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

// 监听扩展安装或更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('扩展已安装 - 时间:', new Date().toISOString());
  } else if (details.reason === 'update') {
    console.log('扩展已更新 - 时间:', new Date().toISOString());
  }
});

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('收到消息:', message);
  console.log('发送者:', sender);
  sendResponse({ status: 'received' });
}); 