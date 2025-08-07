import { FileRecord, FileListResponse, UploadResponse } from './types/file';

// API 基础配置
const API_BASE_URL = '/api';

// 通用请求函数
const request = async <T>(
  url: string, 
  options: RequestInit = {}
): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// 获取文件列表
export const getFileList = (token: string): Promise<FileListResponse> => {
  return request<FileListResponse>('/files/list', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
};

// 上传文件
export const uploadFile = (
  file: File, 
  token: string
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  return fetch(`${API_BASE_URL}/files/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  }).then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  });
};

// 删除文件
export const deleteFile = (
  fileId: number, 
  token: string
): Promise<{ success: boolean; message: string }> => {
  return request(`/files/delete/${fileId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
};

// 下载文件
export const downloadFile = async (
  downloadUrl: string, 
  fileName: string, 
  token: string
): Promise<void> => {
  const response = await fetch(downloadUrl, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}; 