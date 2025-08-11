import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { FileOutlined, FileImageOutlined, FilePdfOutlined } from '@ant-design/icons';
import type { FileRecord } from '../types/file';

interface FileStatsProps {
  files: FileRecord[];
}

// 文件统计信息组件
const FileStats: React.FC<FileStatsProps> = ({ files }) => {
  // 计算文件类型统计
  const getFileTypeStats = () => {
    const stats = {
      total: files.length,
      images: 0,
      documents: 0,
      others: 0,
    };

    files.forEach(file => {
      if (file.file_type.startsWith('image/')) {
        stats.images++;
      } else if (file.file_type.includes('pdf') || 
                 file.file_type.includes('word') || 
                 file.file_type.includes('excel')) {
        stats.documents++;
      } else {
        stats.others++;
      }
    });

    return stats;
  };

  // 计算总文件大小
  const getTotalSize = () => {
    const totalBytes = files.reduce((sum, file) => sum + file.file_size, 0);
    return formatFileSize(totalBytes);
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const stats = getFileTypeStats();

  return (
    <Card style={{ marginBottom: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Statistic
            title="总文件数"
            value={stats.total}
            prefix={<FileOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="图片文件"
            value={stats.images}
            prefix={<FileImageOutlined style={{ color: '#52c41a' }} />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="文档文件"
            value={stats.documents}
            prefix={<FilePdfOutlined style={{ color: '#ff4d4f' }} />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="总大小"
            value={getTotalSize()}
            prefix={<FileOutlined />}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default FileStats; 