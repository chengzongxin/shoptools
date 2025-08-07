import React, { useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import { 
  Card, 
  Upload, 
  Button, 
  Table, 
  Space, 
  Typography,
  Tag,
  Tooltip
} from 'antd';
import { 
  UploadOutlined, 
  DownloadOutlined, 
  DeleteOutlined, 
  FileOutlined,
  FileImageOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { FileManagerStore } from './stores/FileManagerStore';
import type { FileRecord } from './types/file';
import FileStats from './components/FileStats';
import type { UploadProps } from 'antd/es/upload/interface';

const { Title, Text } = Typography;

// 文件管理页面组件
const FileManager: React.FC = observer(() => {
  const { token } = useAuth();
  const store = new FileManagerStore();

  // 组件挂载时获取文件列表
  useEffect(() => {
    if (token) {
      store.fetchFileList(token);
    }
  }, [token]);

  // 文件上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    showUploadList: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      if (token) {
        await store.uploadFile(file as File, token, onSuccess, onError);
      }
    },
  };

  // 表格列定义
  const columns = [
    {
      title: '文件名',
      dataIndex: 'original_name',
      key: 'original_name',
      render: (text: string, record: FileRecord) => (
        <Space>
          {store.getFileIcon(record.file_type)}
          <Tooltip title={text}>
            <Text ellipsis style={{ maxWidth: 200 }}>
              {text}
            </Text>
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => store.formatFileSize(size),
      width: 100,
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (type: string) => (
        <Tag color="blue">{type}</Tag>
      ),
      width: 120,
    },
    {
      title: '上传者',
      dataIndex: 'uploaded_by',
      key: 'uploaded_by',
      width: 100,
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (time: string) => new Date(time).toLocaleString(),
      width: 150,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: FileRecord) => (
        <Space size="small">
          <Tooltip title="下载">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              onClick={() => token && store.handleDownload(record, token)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => token && store.handleDelete(record, token)}
              size="small"
            />
          </Tooltip>
        </Space>
      ),
      width: 100,
    },
  ];

  return (
    <div style={{ padding: 20 }}>
      {/* 文件统计信息 */}
      <FileStats files={store.fileList} />
      
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={3} style={{ margin: 0 }}>
            文件管理
          </Title>
          <Space>
            <Upload {...uploadProps}>
              <Button 
                type="primary" 
                icon={<UploadOutlined />} 
                loading={store.uploadLoading}
              >
                上传文件
              </Button>
            </Upload>
            <Button onClick={() => token && store.fetchFileList(token)} loading={store.loading}>
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={store.fileList}
          rowKey="id"
          loading={store.loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个文件`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>
    </div>
  );
});

export default FileManager; 