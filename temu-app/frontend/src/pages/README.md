# 文件管理模块

## 概述

这是一个基于 React + TypeScript + MobX + Ant Design 的文件管理系统，提供了完整的文件上传、下载、删除和列表展示功能。

## 技术栈

- **React 19** - 前端框架
- **TypeScript** - 类型安全
- **MobX** - 状态管理
- **Ant Design** - UI 组件库
- **React Router** - 路由管理

## 项目结构

```
frontend/src/pages/
├── FileManager.tsx              # 主页面组件
├── api.ts                       # API 接口封装
├── types/
│   └── file.ts                  # 类型定义
├── stores/
│   └── FileManagerStore.ts      # MobX Store
└── components/
    └── FileStats.tsx            # 文件统计组件
```

## 核心功能

### 1. 文件列表展示
- 表格形式展示文件信息
- 支持分页和排序
- 文件类型图标显示
- 文件大小格式化

### 2. 文件上传
- 支持多文件上传
- 拖拽上传
- 上传进度显示
- 文件类型验证

### 3. 文件下载
- 点击下载按钮
- 自动文件命名
- 下载进度提示

### 4. 文件删除
- 确认对话框
- 批量删除支持
- 删除后自动刷新

### 5. 文件统计
- 总文件数统计
- 按类型分组统计
- 总文件大小计算

## 架构设计

### MVVM 模式
- **Model**: `FileManagerStore` - 数据模型和业务逻辑
- **View**: `FileManager.tsx` - 用户界面
- **ViewModel**: Store 与 View 的绑定

### 状态管理
使用 MobX 进行响应式状态管理：

```typescript
export class FileManagerStore {
  @observable fileList: FileRecord[] = [];
  @observable loading: boolean = false;
  
  @action
  async fetchFileList(token: string) {
    // 获取文件列表逻辑
  }
}
```

### 类型安全
完整的 TypeScript 类型定义：

```typescript
interface FileRecord {
  id: number;
  original_name: string;
  file_size: number;
  file_type: string;
  uploaded_by: string;
  upload_time: string;
  download_url: string;
}
```

## 使用方法

### 1. 基本使用
```typescript
import FileManager from './pages/FileManager';

function App() {
  return <FileManager />;
}
```

### 2. 自定义配置
```typescript
// 在 Store 中自定义配置
const store = new FileManagerStore();
store.setMaxFileSize(10 * 1024 * 1024); // 10MB
store.setAllowedTypes(['image/*', 'application/pdf']);
```

## API 接口

### 获取文件列表
```typescript
GET /api/files/list
Authorization: Bearer <token>
```

### 上传文件
```typescript
POST /api/files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

### 删除文件
```typescript
DELETE /api/files/delete/{fileId}
Authorization: Bearer <token>
```

### 下载文件
```typescript
GET /api/files/download/{fileId}
Authorization: Bearer <token>
```

## 组件说明

### FileManager
主页面组件，包含文件管理的完整功能。

### FileStats
文件统计组件，显示文件数量、类型分布等信息。

### FileManagerStore
MobX Store，管理文件相关的状态和业务逻辑。

## 开发指南

### 1. 添加新功能
1. 在 `types/file.ts` 中添加类型定义
2. 在 `api.ts` 中添加 API 接口
3. 在 `FileManagerStore.ts` 中添加业务逻辑
4. 在 `FileManager.tsx` 中添加 UI 组件

### 2. 自定义样式
使用 Ant Design 的主题系统或直接修改 CSS：

```typescript
// 自定义主题
import { ConfigProvider } from 'antd';

<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#00b96b',
    },
  }}
>
  <FileManager />
</ConfigProvider>
```

### 3. 错误处理
所有 API 调用都包含完整的错误处理：

```typescript
try {
  await store.uploadFile(file, token);
  message.success('上传成功');
} catch (error) {
  message.error('上传失败');
  console.error(error);
}
```

## 性能优化

### 1. 虚拟滚动
对于大量文件，可以使用虚拟滚动：

```typescript
import { List } from 'antd';

<List
  virtual
  height={400}
  itemHeight={54}
  data={fileList}
  renderItem={renderFileItem}
/>
```

### 2. 懒加载
图片文件可以使用懒加载：

```typescript
import { Image } from 'antd';

<Image
  lazy
  src={file.url}
  alt={file.name}
/>
```

### 3. 缓存策略
使用 MobX 的响应式特性进行智能更新：

```typescript
@computed
get sortedFiles() {
  return this.fileList.slice().sort((a, b) => 
    new Date(b.upload_time).getTime() - new Date(a.upload_time).getTime()
  );
}
```

## 测试

### 单元测试
```typescript
import { render, screen } from '@testing-library/react';
import FileManager from './FileManager';

test('renders file manager', () => {
  render(<FileManager />);
  expect(screen.getByText('文件管理')).toBeInTheDocument();
});
```

### 集成测试
```typescript
test('uploads file successfully', async () => {
  // 测试文件上传功能
});
```

## 部署

### 构建
```bash
npm run build
```

### 环境变量
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_MAX_FILE_SIZE=10485760
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 