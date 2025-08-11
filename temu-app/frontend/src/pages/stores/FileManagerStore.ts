import { makeAutoObservable } from 'mobx';
import { message, Modal } from 'antd';
import { 
  FileOutlined,
  FileImageOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined
} from '@ant-design/icons';
import type { FileRecord, UploadCallback, UploadErrorCallback } from '../types/file';
import { getFileList, uploadFile, deleteFile, downloadFile } from '../api';

export class FileManagerStore {
  // 响应式数据属性
  fileList: FileRecord[] = [];
  loading: boolean = false;
  uploadLoading: boolean = false;

  constructor() {
    // 使用 makeAutoObservable 自动处理响应式
    makeAutoObservable(this);
  }

  // 获取文件列表
  async fetchFileList(token: string) {
    this.loading = true;
    try {
      const response = await getFileList(token);
      this.fileList = response.data || [];
    } catch (error) {
      console.error('获取文件列表错误:', error);
      message.error('获取文件列表失败');
    } finally {
      this.loading = false;
    }
  }

  // 上传文件
  async uploadFile(
    file: File, 
    token: string, 
    onSuccess?: UploadCallback, 
    onError?: UploadErrorCallback
  ) {
    this.uploadLoading = true;
    try {
      const result = await uploadFile(file, token);
      message.success(`${file.name} 上传成功`);
      onSuccess?.(result);
      // 刷新文件列表
      await this.fetchFileList(token);
    } catch (error) {
      console.error('上传错误:', error);
      message.error(`${file.name} 上传失败`);
      onError?.(error as Error);
    } finally {
      this.uploadLoading = false;
    }
  }

  // 下载文件
  async handleDownload(file: FileRecord, token: string) {
    try {
      await downloadFile(file.download_url, file.original_name, token);
      message.success('文件下载成功');
    } catch (error) {
      console.error('下载错误:', error);
      message.error('文件下载失败');
    }
  }

  // 删除文件
  async handleDelete(file: FileRecord, token: string) {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${file.original_name}" 吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteFile(file.id, token);
          message.success('文件删除成功');
          // 刷新文件列表
          await this.fetchFileList(token);
        } catch (error) {
          console.error('删除错误:', error);
          message.error('文件删除失败');
        }
      },
    });
  }

  // 获取文件图标类型
  getFileIconType(fileType: string): string {
    if (fileType.startsWith('image/')) {
      return 'image';
    } else if (fileType.includes('pdf')) {
      return 'pdf';
    } else if (fileType.includes('word') || fileType.includes('document')) {
      return 'word';
    } else if (fileType.includes('excel') || fileType.includes('spreadsheet')) {
      return 'excel';
    } else {
      return 'file';
    }
  }

  // 格式化文件大小
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // 计算属性：文件总数
  get totalFiles(): number {
    return this.fileList.length;
  }

  // 计算属性：按类型分组的文件
  get filesByType() {
    const grouped = this.fileList.reduce((acc, file) => {
      const type = file.file_type;
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(file);
      return acc;
    }, {} as Record<string, FileRecord[]>);
    
    return grouped;
  }
} 