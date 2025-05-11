/**
 * 图片链接复制工具 v1.2.0
 * 
 * 更新日志：
 * v1.2.0 (2024-03-21)
 * - 修复存储限制导致的链接丢失问题
 * - 优化存储机制，使用双重备份
 * - 提升数据安全性
 * 
 * v1.1.0
 * - 添加记事本功能
 * - 支持链接管理
 * - 添加复制全部功能
 * 
 * v1.0.0
 * - 初始版本
 * - 支持图片链接复制
 * - 支持自动显示按钮
 */

// 创建插件的命名空间
window.ImageCopyPlugin = window.ImageCopyPlugin || {
    version: '1.2.0',
    enabled: true, // 添加全局开关状态
    initialized: false,
    autoShowButton: false,
    notepad: null,
    observer: null
};

// 调试日志函数
function log(message, type = 'info') {
    const prefix = '[图片复制插件]';
    switch(type) {
        case 'error':
            console.error(prefix, message);
            break;
        case 'warn':
            console.warn(prefix, message);
            break;
        default:
            console.log(prefix, message);
    }
}

// 创建全局提示框
function createToast() {
    const toast = document.createElement('div');
    toast.id = '_globalToast';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        font-size: 14px;
        color: white;
        z-index: 1000000;
        opacity: 0;
        transform: translateY(-20px);
        transition: all 0.3s ease;
        pointer-events: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    `;
    document.body.appendChild(toast);
    return toast;
}

// 显示提示信息
function showToast(message, type = 'success') {
    let toast = document.getElementById('_globalToast');
    if (!toast) {
        toast = createToast();
    }

    // 设置样式
    toast.style.backgroundColor = type === 'success' ? '#4285f4' : '#f44336';
    
    // 设置内容
    toast.textContent = message;
    
    // 显示提示
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    // 2秒后隐藏
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
    }, 2000);
}

// 创建复制按钮
function createCopyButton() {
    const button = document.createElement('button');
    button.className = 'copy-link-button';
    button.innerHTML = '复制链接';
    
    // 设置按钮样式
    Object.assign(button.style, {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: '999999',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        padding: '6px 12px',
        fontSize: '12px',
        cursor: 'pointer',
        pointerEvents: 'auto',
        transition: 'all 0.2s ease',
        opacity: '0',
        transform: 'translateY(-10px)',
        minWidth: '70px' // 确保按钮宽度不会因为文字变化而改变
    });

    // 添加悬停效果
    button.addEventListener('mouseenter', () => {
        if (button.innerHTML === '复制链接') {
            button.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        }
    });
    button.addEventListener('mouseleave', () => {
        if (button.innerHTML === '复制链接') {
            button.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        }
    });

    return button;
}

// 创建按钮容器
function createButtonContainer() {
    const container = document.createElement('div');
    Object.assign(container.style, {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: '999999',
        pointerEvents: 'none'
    });
    return container;
}

// 创建记事本
function createNotepad() {
    try {
        const notepad = document.createElement('div');
        notepad.className = '_notepad';
        notepad.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            height: 400px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: none;
            flex-direction: column;
            z-index: 999999;
            resize: both;
            overflow: auto;
            font-size: 12px;
        `;

        const titleBar = document.createElement('div');
        titleBar.className = '_notepadTitle';
        titleBar.style.cssText = `
            padding: 8px;
            background: #f5f5f5;
            border-bottom: 1px solid #ddd;
            cursor: move;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        `;

        const titleText = document.createElement('span');
        titleText.textContent = '链接记事本';
        titleText.style.cssText = `
            font-weight: bold;
            color: #333;
            display: flex;
            align-items: center;
            gap: 4px;
        `;

        // 添加版本号
        const versionText = document.createElement('span');
        versionText.textContent = `v${window.ImageCopyPlugin.version}`;
        versionText.style.cssText = `
            font-size: 10px;
            color: #666;
            background: #f0f0f0;
            padding: 1px 3px;
            border-radius: 2px;
            font-weight: normal;
            margin-left: -2px;
        `;
        titleText.appendChild(versionText);

        const controls = document.createElement('div');
        controls.style.cssText = `
            display: flex;
            gap: 8px;
            align-items: center;
        `;

        // 添加复制全部按钮
        const copyAllBtn = document.createElement('button');
        copyAllBtn.textContent = '复制全部';
        copyAllBtn.title = '复制所有链接';
        copyAllBtn.style.cssText = `
            padding: 2px 6px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
            font-size: 12px;
            color: #4285f4;
        `;
        copyAllBtn.onclick = async () => {
            const links = Array.from(notepad.querySelectorAll('._notepadContent a')).map(a => a.href);
            if (links.length > 0) {
                const allLinks = links.join('\n');
                try {
                    await navigator.clipboard.writeText(allLinks);
                    // 在记事本中间显示提示
                    const message = document.createElement('div');
                    message.textContent = '已复制 ' + links.length + ' 个链接！';
                    message.style.cssText = `
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: rgba(66, 133, 244, 0.9);
                        color: white;
                        padding: 12px 24px;
                        border-radius: 4px;
                        font-size: 14px;
                        text-align: center;
                        z-index: 1000;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                        pointer-events: none;
                    `;
                    notepad.appendChild(message);
                    setTimeout(() => message.remove(), 2000);
                } catch (error) {
                    const message = document.createElement('div');
                    message.textContent = '复制失败：' + error.message;
                    message.style.cssText = `
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: rgba(244, 67, 54, 0.9);
                        color: white;
                        padding: 12px 24px;
                        border-radius: 4px;
                        font-size: 14px;
                        text-align: center;
                        z-index: 1000;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                        pointer-events: none;
                    `;
                    notepad.appendChild(message);
                    setTimeout(() => message.remove(), 2000);
                }
            } else {
                const message = document.createElement('div');
                message.textContent = '记事本为空！';
                message.style.cssText = `
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: rgba(244, 67, 54, 0.9);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 4px;
                    font-size: 14px;
                    text-align: center;
                    z-index: 1000;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                    pointer-events: none;
                `;
                notepad.appendChild(message);
                setTimeout(() => message.remove(), 2000);
            }
        };

        // 添加清空按钮
        const clearBtn = document.createElement('button');
        clearBtn.textContent = '清空';
        clearBtn.title = '清空所有链接';
        clearBtn.style.cssText = `
            padding: 2px 6px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
            font-size: 12px;
            color: #f44336;
        `;
        clearBtn.onclick = () => {
            // 创建确认对话框
            const confirmDialog = document.createElement('div');
            confirmDialog.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 1000001;
                text-align: center;
                min-width: 200px;
            `;
            
            const message = document.createElement('p');
            message.textContent = '确定要清空所有链接吗？';
            message.style.marginBottom = '15px';
            
            const buttonContainer = document.createElement('div');
            buttonContainer.style.cssText = `
                display: flex;
                gap: 10px;
                justify-content: center;
            `;
            
            const confirmBtn = document.createElement('button');
            confirmBtn.textContent = '确定';
            confirmBtn.style.cssText = `
                padding: 5px 15px;
                background: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            `;
            
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = '取消';
            cancelBtn.style.cssText = `
                padding: 5px 15px;
                background: #ccc;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            `;
            
            confirmBtn.onclick = () => {
                const content = notepad.querySelector('._notepadContent');
                content.innerHTML = '';
                confirmDialog.remove();
                showToast('已清空所有链接！', 'success');
            };
            
            cancelBtn.onclick = () => {
                confirmDialog.remove();
            };
            
            buttonContainer.appendChild(confirmBtn);
            buttonContainer.appendChild(cancelBtn);
            confirmDialog.appendChild(message);
            confirmDialog.appendChild(buttonContainer);
            document.body.appendChild(confirmDialog);
        };

        // 添加最小化按钮
        const minimizeBtn = document.createElement('button');
        minimizeBtn.textContent = '_';
        minimizeBtn.title = '最小化';
        minimizeBtn.style.cssText = `
            padding: 2px 6px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
        `;
        minimizeBtn.onclick = () => {
            notepad.style.display = 'none';
        };

        const zoomInBtn = document.createElement('button');
        zoomInBtn.textContent = '+';
        zoomInBtn.title = '放大';
        zoomInBtn.style.cssText = `
            padding: 2px 6px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
        `;
        zoomInBtn.onclick = () => {
            const currentWidth = parseInt(notepad.style.width);
            const currentHeight = parseInt(notepad.style.height);
            notepad.style.width = (currentWidth + 50) + 'px';
            notepad.style.height = (currentHeight + 50) + 'px';
        };

        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.textContent = '-';
        zoomOutBtn.title = '缩小';
        zoomOutBtn.style.cssText = zoomInBtn.style.cssText;
        zoomOutBtn.onclick = () => {
            const currentWidth = parseInt(notepad.style.width);
            const currentHeight = parseInt(notepad.style.height);
            if (currentWidth > 200 && currentHeight > 200) {
                notepad.style.width = (currentWidth - 50) + 'px';
                notepad.style.height = (currentHeight - 50) + 'px';
            }
        };

        controls.appendChild(copyAllBtn);
        controls.appendChild(clearBtn);
        controls.appendChild(zoomInBtn);
        controls.appendChild(zoomOutBtn);
        controls.appendChild(minimizeBtn);
        titleBar.appendChild(titleText);
        titleBar.appendChild(controls);

        const content = document.createElement('div');
        content.className = '_notepadContent';
        content.style.cssText = `
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            font-size: 12px;
        `;

        notepad.appendChild(titleBar);
        notepad.appendChild(content);
        document.body.appendChild(notepad);

        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;

        titleBar.addEventListener('mousedown', (e) => {
            isDragging = true;
            initialX = e.clientX - notepad.offsetLeft;
            initialY = e.clientY - notepad.offsetTop;
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                notepad.style.left = currentX + 'px';
                notepad.style.top = currentY + 'px';
                notepad.style.right = 'auto';
                notepad.style.bottom = 'auto';
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        return { notepad, content };
    } catch (error) {
        log('创建记事本失败: ' + error.message, 'error');
        return null;
    }
}

// 显示记事本
function showNotepad() {
    try {
        if (window.ImageCopyPlugin.notepad) {
            window.ImageCopyPlugin.notepad.notepad.style.display = 'flex';
            log('记事本已显示');
        }
    } catch (error) {
        log('显示记事本失败: ' + error.message, 'error');
    }
}

// 隐藏记事本
function hideNotepad() {
    try {
        if (window.ImageCopyPlugin.notepad) {
            window.ImageCopyPlugin.notepad.notepad.style.display = 'none';
            log('记事本已隐藏');
        }
    } catch (error) {
        log('隐藏记事本失败: ' + error.message, 'error');
    }
}

// 保存链接到存储
function saveLinksToStorage() {
    return new Promise((resolve, reject) => {
        try {
            if (window.ImageCopyPlugin.notepad) {
                const content = window.ImageCopyPlugin.notepad.content;
                const links = Array.from(content.querySelectorAll('a')).map(a => a.href);
                
                // 数据验证
                if (!Array.isArray(links)) {
                    log('保存的链接数据格式错误', 'error');
                    reject(new Error('数据格式错误'));
                    return;
                }

                // 记录当前链接数量
                log(`准备保存 ${links.length} 个链接`);
                
                // 保存到 chrome.storage
                chrome.storage.local.set({ 'savedLinks': links }, function() {
                    if (chrome.runtime.lastError) {
                        log('保存链接失败: ' + chrome.runtime.lastError.message, 'error');
                        reject(chrome.runtime.lastError);
                    } else {
                        log(`成功保存 ${links.length} 个链接`);
                        resolve(links);
                    }
                });
            } else {
                reject(new Error('记事本不存在'));
            }
        } catch (error) {
            log('保存链接失败: ' + error.message, 'error');
            reject(error);
        }
    });
}

// 从存储加载链接
function loadLinksFromStorage() {
    return new Promise((resolve, reject) => {
        try {
            log('开始从存储加载链接...');
            
            chrome.storage.local.get(['savedLinks'], function(result) {
                if (chrome.runtime.lastError) {
                    log('加载链接失败: ' + chrome.runtime.lastError.message, 'error');
                    reject(chrome.runtime.lastError);
                    return;
                }

                if (result.savedLinks && Array.isArray(result.savedLinks) && result.savedLinks.length > 0) {
                    log(`从存储读取到 ${result.savedLinks.length} 个链接`);
                    
                    // 验证链接数据
                    const validLinks = result.savedLinks.filter(link => typeof link === 'string' && link.startsWith('http'));
                    log(`验证后有效链接数量: ${validLinks.length}`);
                    
                    if (validLinks.length !== result.savedLinks.length) {
                        log(`发现 ${result.savedLinks.length - validLinks.length} 个无效链接`, 'warn');
                    }
                    
                    // 清空当前记事本内容
                    if (window.ImageCopyPlugin.notepad) {
                        window.ImageCopyPlugin.notepad.content.innerHTML = '';
                    }
                    
                    // 添加所有有效的链接
                    validLinks.forEach(link => {
                        addToNotepad(link);
                    });
                    
                    // 如果有效链接数量与原始数量不同，更新存储
                    if (validLinks.length !== result.savedLinks.length) {
                        log('更新存储中的链接数据...');
                        chrome.storage.local.set({ 'savedLinks': validLinks });
                    }
                    
                    resolve(validLinks);
                } else {
                    resolve([]);
                }
            });
        } catch (error) {
            log('从存储加载链接失败: ' + error.message, 'error');
            reject(error);
        }
    });
}

// 添加链接到记事本
async function addToNotepad(link) {
    try {
        if (!window.ImageCopyPlugin.notepad) {
            window.ImageCopyPlugin.notepad = createNotepad();
        }

        const content = window.ImageCopyPlugin.notepad.content;
        const linkCount = content.children.length + 1;
        log(`准备添加第 ${linkCount} 个链接: ${link}`);

        // 创建链接容器
        const linkContainer = document.createElement('div');
        linkContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            padding: 2px;
            border-bottom: 1px solid #eee;
        `;

        // 创建序号
        const number = document.createElement('span');
        number.textContent = `${linkCount}.`;
        number.style.cssText = `
            color: #666;
            min-width: 24px;
        `;

        // 创建链接文本
        const linkText = document.createElement('a');
        linkText.href = link;
        linkText.textContent = link;
        linkText.target = '_blank';
        linkText.style.cssText = `
            color: #0066cc;
            text-decoration: none;
            flex: 1;
            word-break: break-all;
            font-size: 12px;
            line-height: 1.2;
        `;

        // 创建删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '删除';
        deleteBtn.title = '删除此链接';
        deleteBtn.style.cssText = `
            padding: 2px 6px;
            border: 1px solid #ccc;
            background: white;
            cursor: pointer;
            border-radius: 4px;
            font-size: 12px;
        `;
        deleteBtn.onclick = () => {
            linkContainer.remove();
            // 更新剩余链接的序号
            const links = content.children;
            for (let i = 0; i < links.length; i++) {
                const numSpan = links[i].querySelector('span');
                if (numSpan) {
                    numSpan.textContent = `${i + 1}.`;
                }
            }
            // 保存更新后的链接列表
            saveLinksToStorage();
        };

        // 组装链接容器
        linkContainer.appendChild(number);
        linkContainer.appendChild(linkText);
        linkContainer.appendChild(deleteBtn);
        content.appendChild(linkContainer);

        // 获取所有当前链接
        const currentLinks = Array.from(content.querySelectorAll('a')).map(a => a.href);
        log(`当前记事本共有 ${currentLinks.length} 个链接`);
        
        // 等待保存完成
        await saveLinksToStorage();
        log(`第 ${linkCount} 个链接添加完成`);

    } catch (error) {
        log('添加链接到记事本失败: ' + error.message, 'error');
    }
}

// 复制链接到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        // 显示复制成功提示
        const tooltip = document.createElement('div');
        tooltip.className = 'copy-tooltip';
        tooltip.textContent = '已复制！';
        
        // 使用更明显的样式
        Object.assign(tooltip.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            backgroundColor: '#4285f4',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '4px',
            fontSize: '14px',
            zIndex: '1000000',
            pointerEvents: 'none',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
            fontWeight: 'bold'
        });

        document.body.appendChild(tooltip);
        
        // 2秒后移除提示
        setTimeout(() => {
            tooltip.remove();
        }, 2000);
        log('链接已复制到剪贴板');
    } catch (err) {
        log('复制失败: ' + err.message, 'error');
    }
}

// 查找最近的父级a标签
function findParentAnchor(element) {
    try {
        let current = element;
        while (current && current !== document.body) {
            if (current.tagName === 'A') {
                return current;
            }
            current = current.parentElement;
        }
        return null;
    } catch (error) {
        log('查找父级a标签失败: ' + error.message, 'error');
        return null;
    }
}

// 处理复制链接点击事件
function handleCopyClick(img) {
    try {
        // 阻止事件冒泡和默认行为
        event.preventDefault();
        event.stopPropagation();

        // 获取按钮元素
        const button = img._buttonContainer.querySelector('.copy-link-button');
        
        // 如果已经复制过，直接返回
        if (button.innerHTML === '已复制') {
            return;
        }

        // 查找父级a标签
        const parentAnchor = findParentAnchor(img);
        let link = '';
        
        if (parentAnchor && parentAnchor.href) {
            link = parentAnchor.href;
        } else if (img.src) {
            link = img.src;
        } else {
            log('未找到可复制的链接', 'warn');
            return;
        }

        // 复制到剪贴板
        copyToClipboard(link);
        
        // 确保记事本存在
        if (!window.ImageCopyPlugin.notepad) {
            window.ImageCopyPlugin.notepad = createNotepad();
        }
        
        // 添加到记事本
        addToNotepad(link);
        
        // 立即保存到存储
        saveLinksToStorage();
        
        log('已复制链接: ' + link);

        // 修改按钮文字和样式
        button.innerHTML = '已复制';
        button.style.backgroundColor = 'rgba(76, 175, 80, 0.8)'; // 绿色背景

    } catch (error) {
        log('处理复制点击事件时出错', error, 'error');
    }
}

// 处理鼠标进入图片事件
function handleMouseEnter(event) {
    try {
        const img = event.target;
        log('鼠标进入图片', img.src);

        // 检查是否已经有按钮
        if (img._buttonContainer) {
            return;
        }

        // 创建按钮容器
        const container = createButtonContainer();
        img._buttonContainer = container;
        img.parentNode.insertBefore(container, img.nextSibling);

        // 创建按钮
        const button = createCopyButton();
        container.appendChild(button);

        // 显示按钮
        requestAnimationFrame(() => {
            button.style.opacity = '1';
            button.style.transform = 'translateY(0)';
        });

        // 添加点击事件
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleCopyClick(img);
        });

        // 修改图片的mouseleave事件处理
        const originalMouseLeave = img.onmouseleave;
        img.onmouseleave = (e) => {
            // 检查鼠标是否在按钮容器内
            const rect = container.getBoundingClientRect();
            const x = e.clientX;
            const y = e.clientY;
            
            if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
                return; // 如果鼠标在容器内，不触发mouseleave
            }
            
            if (originalMouseLeave) {
                originalMouseLeave.call(img, e);
            }
            handleMouseLeave(img);
        };

    } catch (error) {
        log('处理鼠标进入事件时出错', error, 'error');
    }
}

// 处理鼠标离开图片事件
function handleMouseLeave(img) {
    try {
        log('鼠标离开图片', img.src);
        
        // 如果启用了自动显示，不移除按钮
        if (window.ImageCopyPlugin.autoShowButton) {
            log('自动显示已启用，保持按钮显示');
            return;
        }
        
        // 检查按钮容器是否存在
        if (img._buttonContainer) {
            const button = img._buttonContainer.querySelector('.copy-link-button');
            if (button) {
                // 添加淡出动画
                button.style.opacity = '0';
                button.style.transform = 'translateY(-10px)';
                
                // 等待动画完成后移除
                setTimeout(() => {
                    if (img._buttonContainer && img._buttonContainer.parentNode) {
                        img._buttonContainer.parentNode.removeChild(img._buttonContainer);
                        img._buttonContainer = null;
                    }
                }, 200);
            }
        }
    } catch (error) {
        log('处理鼠标离开事件时出错', error, 'error');
    }
}

// 为图片添加事件监听器
function addImageListeners() {
    try {
        // 获取所有图片元素
        const images = document.querySelectorAll('img');
        const newImages = Array.from(images).filter(img => !img.hasAttribute('data-copy-listener'));
        
        if (newImages.length > 0) {
            log(`为 ${newImages.length} 个新图片添加事件监听器`);
            
            // 为每个新图片添加事件监听器
            newImages.forEach(img => {
                img.setAttribute('data-copy-listener', 'true');
                img.addEventListener('mouseenter', handleMouseEnter);
                img.addEventListener('mouseleave', handleMouseLeave);
            });
        }
    } catch (error) {
        log('添加图片事件监听器失败: ' + error.message, 'error');
    }
}

// 修改初始化函数
async function initialize() {
    try {
        // 确保document.body存在
        if (!document.body) {
            log('等待DOM加载...', 'warn');
            return;
        }

        // 如果已经初始化过，则不再重复初始化
        if (window.ImageCopyPlugin.initialized) {
            return;
        }

        // 从存储中获取插件状态
        chrome.storage.sync.get(['pluginEnabled', 'autoShowButton'], async function(result) {
            window.ImageCopyPlugin.enabled = result.pluginEnabled !== false; // 默认为启用
            window.ImageCopyPlugin.autoShowButton = result.autoShowButton || false;
            
            if (window.ImageCopyPlugin.enabled) {
                // 创建记事本
                const notepad = createNotepad();
                if (notepad) {
                    window.ImageCopyPlugin.notepad = notepad;
                    log('记事本创建成功');
                    
                    // 等待加载保存的链接
                    await loadLinksFromStorage();
                    
                    // 默认隐藏记事本
                    hideNotepad();
                }

                // 如果启用了自动显示，为所有图片添加按钮
                if (window.ImageCopyPlugin.autoShowButton) {
                    const images = document.querySelectorAll('img');
                    images.forEach(img => {
                        if (!img._buttonContainer) {
                            handleMouseEnter({ target: img });
                        }
                    });
                }

                // 为现有图片添加事件监听器
                addImageListeners();

                // 创建并配置MutationObserver
                setupMutationObserver();
            }
        });
        
        window.ImageCopyPlugin.initialized = true;
        log('插件初始化成功');
    } catch (error) {
        log('初始化失败: ' + error.message, 'error');
    }
}

// 等待DOM加载完成
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// 添加页面完全加载后的处理
window.addEventListener('load', () => {
    if (!window.ImageCopyPlugin.initialized) {
        initialize();
    }
});

// 添加消息监听器
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    try {
        switch (request.action) {
            case 'togglePlugin':
                window.ImageCopyPlugin.enabled = request.value;
                if (request.value) {
                    initialize();
                    sendResponse({ success: true, message: '插件已启用' });
                } else {
                    // 禁用插件时清理所有按钮和记事本
                    const containers = document.querySelectorAll('._buttonContainer');
                    containers.forEach(container => {
                        if (container.parentNode) {
                            container.parentNode.removeChild(container);
                        }
                    });
                    if (window.ImageCopyPlugin.notepad) {
                        window.ImageCopyPlugin.notepad.notepad.remove();
                        window.ImageCopyPlugin.notepad = null;
                    }
                    sendResponse({ success: true, message: '插件已禁用' });
                }
                break;

            case 'toggleNotepad':
                if (window.ImageCopyPlugin.enabled && window.ImageCopyPlugin.notepad) {
                    const isVisible = window.ImageCopyPlugin.notepad.notepad.style.display === 'flex';
                    if (isVisible) {
                        hideNotepad();
                        sendResponse({ success: true, message: '记事本已隐藏' });
                    } else {
                        showNotepad();
                        sendResponse({ success: true, message: '记事本已显示' });
                    }
                } else {
                    sendResponse({ success: false, message: '插件未启用或记事本未初始化' });
                }
                break;

            case 'showNotepad':
                if (window.ImageCopyPlugin.enabled) {
                    if (!window.ImageCopyPlugin.notepad) {
                        window.ImageCopyPlugin.notepad = createNotepad();
                    }
                    showNotepad();
                    sendResponse({ success: true, message: '记事本已显示' });
                } else {
                    sendResponse({ success: false, message: '插件未启用' });
                }
                break;

            case 'toggleAutoShow':
                if (window.ImageCopyPlugin.enabled) {
                    handleAutoShow(request.value);
                    sendResponse({ 
                        success: true, 
                        message: request.value ? '已启用自动显示' : '已禁用自动显示' 
                    });
                } else {
                    sendResponse({ success: false, message: '插件未启用' });
                }
                break;

            default:
                sendResponse({ success: false, message: '未知的操作类型' });
        }
    } catch (error) {
        log('处理消息时出错: ' + error.message, 'error');
        sendResponse({ success: false, message: '操作失败: ' + error.message });
    }
    return true; // 保持消息通道开放，以便异步响应
});

// 处理自动显示按钮
function handleAutoShow(value) {
    try {
        window.ImageCopyPlugin.autoShowButton = value;
        log('自动显示状态已更新: ' + value);
        
        if (value) {
            // 为所有图片添加按钮
            const images = document.querySelectorAll('img');
            log('找到 ' + images.length + ' 个图片');
            images.forEach(img => {
                if (!img._buttonContainer) {
                    log('为图片添加按钮: ' + img.src);
                    handleMouseEnter({ target: img });
                }
            });
        } else {
            // 移除所有按钮
            const containers = document.querySelectorAll('._buttonContainer');
            log('移除 ' + containers.length + ' 个按钮容器');
            containers.forEach(container => {
                if (container.parentNode) {
                    container.parentNode.removeChild(container);
                }
            });
        }
    } catch (error) {
        log('处理自动显示时出错: ' + error.message, 'error');
    }
}

// 创建并配置MutationObserver
function setupMutationObserver() {
    try {
        if (!window.ImageCopyPlugin.observer) {
            window.ImageCopyPlugin.observer = new MutationObserver((mutations) => {
                try {
                    mutations.forEach((mutation) => {
                        if (mutation.addedNodes.length) {
                            addImageListeners();
                            
                            // 如果启用了自动显示，为新添加的图片添加按钮
                            if (window.ImageCopyPlugin.autoShowButton) {
                                mutation.addedNodes.forEach(node => {
                                    if (node.nodeType === 1) { // 元素节点
                                        const images = node.querySelectorAll('img');
                                        images.forEach(img => {
                                            if (!img._buttonContainer) {
                                                handleMouseEnter({ target: img });
                                            }
                                        });
                                    }
                                });
                            }
                        }
                    });
                } catch (error) {
                    log('处理DOM变化失败: ' + error.message, 'error');
                }
            });

            // 开始观察
            window.ImageCopyPlugin.observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    } catch (error) {
        log('设置MutationObserver失败: ' + error.message, 'error');
    }
} 