// 获取DOM元素
const pluginEnabledSwitch = document.getElementById('pluginEnabled');
const autoShowButtonSwitch = document.getElementById('autoShowButton');
const immersiveButtonSwitch = document.getElementById('immersiveButton');
const toggleNotepadButton = document.getElementById('toggleNotepad');
const statusDiv = document.getElementById('status');
const authorInput = document.getElementById('authorInput');
const addAuthorBtn = document.getElementById('addAuthorBtn');
const blacklistContainer = document.getElementById('blacklistContainer');
const toggleBlacklistBtn = document.getElementById('toggleBlacklistBtn');
const blacklistContent = document.getElementById('blacklistContent');
const blacklistBadge = document.getElementById('blacklistBadge');
const blacklistArrow = document.getElementById('blacklistArrow');

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
chrome.storage.sync.get(['pluginEnabled', 'autoShowButton', 'immersiveButton'], function(result) {
    pluginEnabledSwitch.checked = result.pluginEnabled !== false; // 默认为启用
    autoShowButtonSwitch.checked = result.autoShowButton || false;
    immersiveButtonSwitch.checked = result.immersiveButton || false;
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

// 监听沉浸式按钮开关
immersiveButtonSwitch.addEventListener('change', async function() {
    try {
        const enabled = this.checked;
        await chrome.storage.sync.set({ immersiveButton: enabled });
        const response = await sendMessageToContentScript({
            action: 'toggleImmersiveButton',
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
    
    // 加载黑名单
    loadBlacklist();
});

// 渲染黑名单列表
function renderBlacklist(blacklist) {
    // 更新徽章数字
    if (blacklistBadge) {
        blacklistBadge.textContent = blacklist ? blacklist.length : 0;
    }
    
    if (!blacklist || blacklist.length === 0) {
        blacklistContainer.innerHTML = '<div class="blacklist-empty">暂无黑名单作者</div>';
        return;
    }
    
    blacklistContainer.innerHTML = '';
    blacklist.forEach(author => {
        const item = document.createElement('div');
        item.className = 'blacklist-item';
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'blacklist-item-name';
        nameSpan.textContent = author;
        
        const removeBtn = document.createElement('button');
        removeBtn.textContent = '删除';
        removeBtn.onclick = () => removeAuthor(author);
        
        item.appendChild(nameSpan);
        item.appendChild(removeBtn);
        blacklistContainer.appendChild(item);
    });
}

// 加载黑名单
async function loadBlacklist() {
    try {
        const response = await sendMessageToContentScript({
            action: 'getBlacklist'
        });
        if (response.success) {
            renderBlacklist(response.blacklist);
        }
    } catch (error) {
        console.error('加载黑名单失败:', error);
    }
}

// 添加作者到黑名单（支持批量添加）
async function addAuthor() {
    const input = authorInput.value.trim();
    
    if (!input) {
        showStatus('请输入作者名', true);
        return;
    }
    
    // 解析输入：支持逗号、换行符、分号分隔
    const authors = input
        .split(/[,，\n\r;；]+/)  // 支持中英文逗号、换行符、分号
        .map(a => a.trim())       // 去除首尾空格
        .filter(a => a.length > 0); // 过滤空字符串
    
    if (authors.length === 0) {
        showStatus('请输入有效的作者名', true);
        return;
    }
    
    try {
        let addedCount = 0;
        let skippedCount = 0;
        let finalBlacklist = [];
        
        // 批量添加
        for (const author of authors) {
            try {
                const response = await sendMessageToContentScript({
                    action: 'addToBlacklist',
                    author: author
                });
                
                if (response.success) {
                    addedCount++;
                    finalBlacklist = response.blacklist;
                } else {
                    skippedCount++;
                }
            } catch (error) {
                console.error('添加作者失败:', author, error);
                skippedCount++;
            }
        }
        
        // 显示结果
        if (addedCount > 0) {
            if (skippedCount > 0) {
                showStatus(`成功添加 ${addedCount} 个作者，${skippedCount} 个已存在或失败`);
            } else {
                showStatus(`成功添加 ${addedCount} 个作者`);
            }
            authorInput.value = ''; // 清空输入框
            renderBlacklist(finalBlacklist);
        } else {
            showStatus('所有作者均已存在或添加失败', true);
        }
    } catch (error) {
        showStatus('添加失败: ' + error.message, true);
    }
}

// 从黑名单移除作者
async function removeAuthor(author) {
    try {
        const response = await sendMessageToContentScript({
            action: 'removeFromBlacklist',
            author: author
        });
        
        if (response.success) {
            showStatus(response.message);
            renderBlacklist(response.blacklist);
        } else {
            showStatus(response.message, true);
        }
    } catch (error) {
        showStatus('删除失败: ' + error.message, true);
    }
}

// 监听添加按钮
addAuthorBtn.addEventListener('click', addAuthor);

// 监听回车键
authorInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addAuthor();
    }
});

// 黑名单折叠/展开功能
let isBlacklistExpanded = false;

toggleBlacklistBtn.addEventListener('click', function() {
    isBlacklistExpanded = !isBlacklistExpanded;
    
    if (isBlacklistExpanded) {
        // 展开
        blacklistContent.style.display = 'block';
        blacklistArrow.classList.add('expanded');
    } else {
        // 收起
        blacklistContent.style.display = 'none';
        blacklistArrow.classList.remove('expanded');
    }
}); 