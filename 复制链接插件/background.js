// 监听来自content script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'showNotification') {
        // 创建通知
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icon48.png',
            title: '图片复制插件',
            message: request.message,
            priority: 2
        });
    }
}); 