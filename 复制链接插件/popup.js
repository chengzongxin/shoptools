// 获取DOM元素
const pluginEnabledSwitch = document.getElementById('pluginEnabled');
const autoShowButtonSwitch = document.getElementById('autoShowButton');
const toggleNotepadButton = document.getElementById('toggleNotepad');
const statusDiv = document.getElementById('status');

// 显示状态消息
function showStatus(message, isError = false) {
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + (isError ? 'error' : 'success');
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// 发送消息到content script
function sendMessageToContentScript(message) {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (!tabs[0]) {
                reject(new Error('未找到活动标签页'));
                return;
            }
            
            chrome.tabs.sendMessage(tabs[0].id, message, function(response) {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else if (response && response.success) {
                    resolve(response);
                } else {
                    reject(new Error(response ? response.message : '未知错误'));
                }
            });
        });
    });
}

// 从存储中加载设置
chrome.storage.sync.get(['pluginEnabled', 'autoShowButton'], function(result) {
    pluginEnabledSwitch.checked = result.pluginEnabled !== false; // 默认为启用
    autoShowButtonSwitch.checked = result.autoShowButton || false;
});

// 监听插件启用/禁用开关
pluginEnabledSwitch.addEventListener('change', async function() {
    try {
        const enabled = this.checked;
        await chrome.storage.sync.set({ pluginEnabled: enabled });
        const response = await sendMessageToContentScript({
            action: 'togglePlugin',
            value: enabled
        });
        showStatus(response.message);
    } catch (error) {
        showStatus(error.message, true);
        // 恢复开关状态
        this.checked = !this.checked;
    }
});

// 监听自动显示按钮开关
autoShowButtonSwitch.addEventListener('change', async function() {
    try {
        const enabled = this.checked;
        await chrome.storage.sync.set({ autoShowButton: enabled });
        const response = await sendMessageToContentScript({
            action: 'toggleAutoShow',
            value: enabled
        });
        showStatus(response.message);
    } catch (error) {
        showStatus(error.message, true);
        // 恢复开关状态
        this.checked = !this.checked;
    }
});

// 监听显示/隐藏记事本按钮
toggleNotepadButton.addEventListener('click', async function() {
    try {
        const response = await sendMessageToContentScript({
            action: 'toggleNotepad'
        });
        showStatus(response.message);
    } catch (error) {
        showStatus(error.message, true);
    }
});

// 在popup打开时显示记事本
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await sendMessageToContentScript({
            action: 'showNotepad'
        });
    } catch (error) {
        // 忽略错误，因为可能是content script还没有加载
    }
}); 