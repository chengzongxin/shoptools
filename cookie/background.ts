// 监听cookie变化
chrome.cookies.onChanged.addListener((changeInfo) => {
  console.log('Cookie changed:', changeInfo);
}); 