import { Layout, Menu, Button, Space, Dropdown } from 'antd';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
  useNavigate
} from 'react-router-dom';
import {
  SettingOutlined,
  TableOutlined,
  SearchOutlined,
  PictureOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
  BugOutlined,
  FileOutlined
} from '@ant-design/icons';
import './App.css';
import ProductList from './pages/ProductList';
import ProductDetail from './pages/ProductDetail';
import ProductForm from './pages/ProductForm';
import ConfigPage from './pages/ConfigPage';
import ProductPage from './pages/ProductPage';
import GalleryPage from './pages/GalleryPage';
import UnpublishedRecordsPage from './pages/UnpublishedRecordsPage';
import FileManager from './pages/FileManager';
import SimpleFileTest from './pages/components/SimpleFileTest';
import Login from './pages/Login';
import TestPage from './pages/TestPage';
import ProtectedRoute from './components/ProtectedRoute';
import { ProductListProvider } from './pages/ProductListContext';
import { GlobalNotificationProvider } from './pages/GlobalNotification';
import { UnpublishedRecordsProvider } from './contexts/UnpublishedRecordsContext';
import { ProductSearchProvider } from './pages/ProductSearchContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
// 导入 stagewise 工具栏组件
import { StagewiseToolbar } from '@stagewise/toolbar-react';
import ReactPlugin from '@stagewise-plugins/react';
import '@ant-design/v5-patch-for-react-19';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: 'config', icon: <SettingOutlined />, label: <Link to="/config">配置管理</Link> },
  { key: 'compliance', icon: <TableOutlined />, label: <Link to="/compliance">违规商品</Link> },
  { key: 'product', icon: <SearchOutlined />, label: <Link to="/product">商品搜索</Link> },
  { key: 'gallery', icon: <PictureOutlined />, label: <Link to="/gallery">图库管理</Link> },
  { key: 'files', icon: <FileOutlined />, label: <Link to="/files">文件管理</Link> },
  { key: 'unpublished', icon: <DatabaseOutlined />, label: <Link to="/unpublished">未发布记录</Link> },
  { key: 'test', icon: <BugOutlined />, label: <Link to="/test">测试页面</Link> },
];

// 用户菜单组件
const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: `用户：${user?.username}`,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
      <Button type="text" icon={<UserOutlined />} style={{ color: '#1890ff' }}>
        {user?.username}
      </Button>
    </Dropdown>
  );
};

function AppLayout() {
  const location = useLocation();
  const selectedKey = menuItems.find(item => location.pathname.startsWith(`/${item.key}`))?.key || 'compliance';
  
  return (
    <Layout style={{ minHeight: '100vh', width: '100vw' }}>
      <Sider width={200} style={{ background: '#fff', overflow: 'hidden' }}>
        <div style={{ height: 32, margin: 16, color: '#1890ff', fontWeight: 'bold', fontSize: 18 }}>TEMU工具箱</div>
        <Menu mode="inline" selectedKeys={[selectedKey]} style={{ height: '100%', borderRight: 0 }} items={menuItems} />
      </Sider>
      <Layout>
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <div style={{ fontSize: 20, fontWeight: 'bold' }}>
            TEMU 违规商品&图库管理平台
          </div>
          <UserMenu />
        </Header>
        <Content style={{
          margin: '0',
          background: '#fff',
          padding: 24,
          height: 'calc(100vh - 64px)',
          overflowY: 'auto',
          flex: 1,
        }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/config" element={
              <ProtectedRoute>
                <ConfigPage />
              </ProtectedRoute>
            } />
            <Route path="/compliance" element={
              <ProtectedRoute>
                <ProductList />
              </ProtectedRoute>
            } />
            <Route path="/compliance/new" element={
              <ProtectedRoute>
                <ProductForm />
              </ProtectedRoute>
            } />
            <Route path="/compliance/:spu_id" element={
              <ProtectedRoute>
                <ProductDetail />
              </ProtectedRoute>
            } />
            <Route path="/product" element={
              <ProtectedRoute>
                <ProductPage />
              </ProtectedRoute>
            } />
            <Route path="/gallery" element={
              <ProtectedRoute>
                <GalleryPage />
              </ProtectedRoute>
            } />
            <Route path="/files" element={
              <ProtectedRoute>
                <FileManager />
              </ProtectedRoute>
            } />
            <Route path="/unpublished" element={
              <ProtectedRoute>
                <UnpublishedRecordsPage />
              </ProtectedRoute>
            } />
            <Route path="*" element={
              <ProtectedRoute>
                <ProductList />
              </ProtectedRoute>
            } />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <GlobalNotificationProvider>
          <ProductListProvider>
            <UnpublishedRecordsProvider>
              <ProductSearchProvider>
                <AppLayout />
                {/* 添加 stagewise 工具栏 - 仅在开发模式下显示 */}
                <StagewiseToolbar 
                  config={{
                    plugins: [ReactPlugin]
                  }}
                  enabled={false}
                />
              </ProductSearchProvider>
            </UnpublishedRecordsProvider>
          </ProductListProvider>
        </GlobalNotificationProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
