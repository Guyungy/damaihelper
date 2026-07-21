import { useEffect, useState } from 'react'
import { Card, Col, Row, Statistic, Typography, Button, Space, Alert, Spin, Descriptions, Tag } from 'antd'
import {
  RocketOutlined,
  SettingOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { getAiStatus, getHealth, getTicketLogs } from '../api'

interface Props {
  onNavigate: (key: 'dashboard' | 'config' | 'task' | 'ai') => void
}

export default function DashboardPage({ onNavigate }: Props) {
  const [loading, setLoading] = useState(true)
  const [health, setHealth] = useState<any>(null)
  const [ai, setAi] = useState<any>(null)
  const [task, setTask] = useState<any>(null)
  const [error, setError] = useState('')

  const refresh = async () => {
    setLoading(true)
    setError('')
    try {
      const [h, a, t] = await Promise.all([getHealth(), getAiStatus(), getTicketLogs(0)])
      setHealth(h)
      setAi(a)
      setTask(t)
    } catch (e: any) {
      setError(e?.message || '无法连接后端，请先运行 python web_server.py')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const env = ai?.environment || {}
  const torch = env.torch || {}
  const gpu = env.gpu || {}

  return (
    <Spin spinning={loading}>
      <Typography.Title level={3} className="page-title">
        总览
      </Typography.Title>
      {error && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message="后端未连接"
          description={error}
          action={
            <Button size="small" onClick={refresh}>
              重试
            </Button>
          }
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title="后端状态"
              value={health?.status === 'ok' ? '在线' : '离线'}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: health?.status === 'ok' ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title="任务进度"
              value={task?.progress ?? 0}
              suffix="%"
              prefix={<RocketOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title="CUDA"
              value={torch.cuda_available ? '就绪' : 'CPU/未装'}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: torch.cuda_available ? '#1677ff' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title="YOLO"
              value={ai?.engine?.engine_loaded ? '已加载' : ai?.engine?.mock_mode ? 'Mock' : '未加载'}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card title="本机 AI 环境" extra={<Button type="link" onClick={refresh}>刷新</Button>}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Python">{env.python || '-'}</Descriptions.Item>
              <Descriptions.Item label="GPU">
                {gpu.name ? (
                  <Space>
                    <Tag color="blue">{gpu.name}</Tag>
                    <span className="muted">Driver {gpu.driver}</span>
                  </Space>
                ) : (
                  '未检测到'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="PyTorch">
                {torch.installed ? `${torch.version} · cuda=${String(torch.cuda_available)}` : '未安装'}
              </Descriptions.Item>
              <Descriptions.Item label="设备">{env.recommend_device || '-'}</Descriptions.Item>
              <Descriptions.Item label="说明">{env.message || '-'}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="快捷入口">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button type="primary" block icon={<RocketOutlined />} onClick={() => onNavigate('task')}>
                启动任务编排
              </Button>
              <Button block icon={<SettingOutlined />} onClick={() => onNavigate('config')}>
                编辑配置
              </Button>
              <Button block icon={<ExperimentOutlined />} onClick={() => onNavigate('ai')}>
                YOLO / CUDA 面板
              </Button>
              <Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
                依赖安装：<Typography.Text code>python tools/install_deps.py</Typography.Text>
                <br />
                一键启动：<Typography.Text code>win一键运行.bat</Typography.Text>
              </Typography.Paragraph>
            </Space>
          </Card>
        </Col>
      </Row>
    </Spin>
  )
}
