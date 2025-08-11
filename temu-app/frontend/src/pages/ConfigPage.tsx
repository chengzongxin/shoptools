import React, { useEffect, useState } from "react";
import { Card, Form, Input, Button, message, Alert, Space, Tag, Typography } from "antd";
import { useGlobalNotification } from "./GlobalNotification";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const { Text } = Typography;

interface ConfigData {
  kuajingmaihuo_cookie: string;
  agentseller_cookie: string;
  mallid: string;
  parent_msg_id?: string;
  parent_msg_timestamp?: string;
  tool_id?: string;
}

interface ConfigStatus {
  has_config: boolean;
  config_complete: boolean;
  missing_fields: string[];
  last_updated?: string;
}

const ConfigPage: React.FC = () => {
  const [form] = Form.useForm();
  const notify = useGlobalNotification();
  const { user, token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [configStatus, setConfigStatus] = useState<ConfigStatus | null>(null);

  // 检查认证状态
  useEffect(() => {
    if (!isAuthenticated || !token) {
      notify({ type: 'error', message: "请先登录" });
      navigate('/login');
      return;
    }
  }, [isAuthenticated, token, navigate, notify]);

  // 获取配置状态
  const fetchConfigStatus = async () => {
    if (!token) return;
    
    try {
      const res = await fetch("/api/config/status", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        setConfigStatus(data.data);
      }
    } catch (error) {
      console.error("获取配置状态失败:", error);
    }
  };

  // 获取配置
  const fetchConfig = async () => {
    if (!token) return;
    
    try {
      const res = await fetch("/api/config", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        form.setFieldsValue(data.data);
      }
    } catch (error) {
      console.error("获取配置失败:", error);
    }
  };

  useEffect(() => {
    if (token) {
      fetchConfigStatus();
      fetchConfig();
    }
  }, [token]);

  // 保存配置
  const onFinish = async (values: ConfigData) => {
    if (!token) {
      notify({ type: 'error', message: "请先登录" });
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(values)
      });
      const data = await res.json();
      if (data.success) {
        notify({ type: 'success', message: data.msg || "配置已保存！" });
        // 重新获取配置状态
        await fetchConfigStatus();
      } else {
        notify({ type: 'error', message: data.msg || "保存失败" });
      }
    } catch (error) {
      notify({ type: 'error', message: "保存配置时发生错误" });
    } finally {
      setLoading(false);
    }
  };

  // 清除配置
  const handleClearConfig = async () => {
    if (!token) {
      notify({ type: 'error', message: "请先登录" });
      return;
    }

    const confirmed = window.confirm('确定要清除所有配置吗？此操作不可撤销。');
    if (!confirmed) return;
    
    try {
      setLoading(true);
      const res = await fetch("/api/config", {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        notify({ type: 'success', message: "配置已清除！" });
        form.resetFields();
        await fetchConfigStatus();
      } else {
        notify({ type: 'error', message: data.msg || "清除失败" });
      }
    } catch (error) {
      notify({ type: 'error', message: "清除配置时发生错误" });
    } finally {
      setLoading(false);
    }
  };

  // 如果未认证，显示加载状态
  if (!isAuthenticated || !token) {
    return (
      <Card title="配置管理" style={{ height: 'calc(100vh - 64px - 48px)' }}>
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Text>正在验证登录状态...</Text>
        </div>
      </Card>
    );
  }

  // 渲染配置状态
  const renderConfigStatus = () => {
    if (!configStatus) return null;

    if (!configStatus.has_config) {
      return (
        <Alert
          message="配置未设置"
          description="请填写以下配置信息以开始使用系统"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      );
    }

    return (
      <Alert
        message={
          <Space>
            <span>配置状态</span>
            {configStatus.config_complete ? (
              <Tag color="green">完整</Tag>
            ) : (
              <Tag color="orange">不完整</Tag>
            )}
          </Space>
        }
        description={
          <div>
            {configStatus.config_complete ? (
              <Text type="success">所有必需配置已设置，系统可以正常使用</Text>
            ) : (
              <div>
                <Text type="warning">缺少以下配置项：</Text>
                <br />
                {configStatus.missing_fields.map(field => (
                  <Tag key={field} color="red" style={{ marginTop: 4 }}>
                    {field === 'kuajingmaihuo_cookie' ? '跨境猫卖家中心Cookie' :
                     field === 'agentseller_cookie' ? 'TEMU代理商中心Cookie' :
                     field === 'mallid' ? 'MallId' : field}
                  </Tag>
                ))}
              </div>
            )}
            {configStatus.last_updated && (
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">最后更新：{new Date(configStatus.last_updated).toLocaleString()}</Text>
              </div>
            )}
          </div>
        }
        type={configStatus.config_complete ? "success" : "warning"}
        showIcon
        style={{ marginBottom: 16 }}
      />
    );
  };

  return (
    <Card title="配置管理" style={{ height: 'calc(100vh - 64px - 48px)' }}>
      {renderConfigStatus()}
      
      <Form 
        form={form} 
        labelCol={{ span: 4 }} 
        wrapperCol={{ span: 8 }} 
        onFinish={onFinish}
        layout="vertical"
      >
        <Form.Item 
          label="跨境猫卖家中心Cookie" 
          name="kuajingmaihuo_cookie"
          rules={[{ required: true, message: '请输入跨境猫卖家中心Cookie' }]}
        >
          <Input.TextArea 
            rows={3} 
            placeholder="请输入 https://seller.kuajingmaihuo.com/ 的Cookie信息" 
          />
        </Form.Item>
        
        <Form.Item 
          label="TEMU代理商中心Cookie" 
          name="agentseller_cookie"
          rules={[{ required: true, message: '请输入TEMU代理商中心Cookie' }]}
        >
          <Input.TextArea 
            rows={3} 
            placeholder="请输入 https://agentseller.temu.com/ 的Cookie信息" 
          />
        </Form.Item>
        
        <Form.Item 
          label="MallId" 
          name="mallid"
          rules={[{ required: true, message: '请输入MallId' }]}
        >
          <Input placeholder="请输入MallId" />
        </Form.Item>
        
        <Form.Item>
          <Space>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
            >
              保存配置
            </Button>
            <Button 
              danger 
              onClick={handleClearConfig}
              loading={loading}
            >
              清除配置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ConfigPage; 