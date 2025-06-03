// 定义Cookie接口
interface Cookie {
  name: string;
  value: string;
  domain: string;
  path: string;
}

// 获取当前标签页的URL
async function getCurrentTabUrl(): Promise<string> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab.url || '';
}

// 获取指定URL的所有cookie
async function getAllCookies(url: string): Promise<Cookie[]> {
  return await chrome.cookies.getAll({ url });
}

// 显示cookie列表
function displayCookies(cookies: Cookie[]): void {
  const cookieList = document.getElementById('cookieList');
  if (!cookieList) return;

  cookieList.innerHTML = '';
  
  if (cookies.length === 0) {
    cookieList.innerHTML = '<p>没有找到cookie</p>';
    return;
  }

  cookies.forEach(cookie => {
    const cookieItem = document.createElement('div');
    cookieItem.className = 'cookie-item';
    cookieItem.innerHTML = `
      <strong>${cookie.name}</strong><br>
      值: ${cookie.value}<br>
      域名: ${cookie.domain}<br>
      路径: ${cookie.path}
    `;
    cookieList.appendChild(cookieItem);
  });
}

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
  const getCookiesButton = document.getElementById('getCookies');
  
  if (getCookiesButton) {
    getCookiesButton.addEventListener('click', async () => {
      try {
        const url = await getCurrentTabUrl();
        const cookies = await getAllCookies(url);
        displayCookies(cookies);
      } catch (error) {
        console.error('获取cookie时出错:', error);
        const cookieList = document.getElementById('cookieList');
        if (cookieList) {
          cookieList.innerHTML = '<p>获取cookie时出错</p>';
        }
      }
    });
  }
}); 