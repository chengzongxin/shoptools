import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Ant Design 5.x 不需要手动导入CSS，会自动按需加载
// 如果需要全局样式，可以使用以下方式之一：
// import 'antd/dist/reset.css'  // 重置样式
// import 'antd/dist/antd.variable.css'  // 变量样式
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
