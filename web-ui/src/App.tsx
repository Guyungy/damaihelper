import { useEffect, useMemo, useState } from 'react'
import {
  Layout,
  Menu,
  Typography,
  theme,
  Space,
  Tag,
  Badge,
} from 'antd'
import {
  DashboardOutlined,
  SettingOutlined,
  RocketOutlined,
  ExperimentOutlined,
  CloudServerOutlined,
} from '@ant-design/icons'
import DashboardPage from './pages/DashboardPage'
import ConfigPage from './pages/ConfigPage'
import TaskPage from './pages/TaskPage'
import AiPage from './pages/AiPage'
import { getHealth } from './api'

const { Header, Sider, Content } = Layout

type PageKey = 'dashboard' | 'config' | 'task' | 'ai'

export default function App() {
  const [page, setPage] = useState<PageKey>('dashboard')
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)
  const [busy, setBusy] = useState(false)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  useEffect(() => {
    let cancelled = false
    const tick = async () => {
      try {
        const h = await getHealth()
        if (!cancelled) {
          setBackendOnline(h?.status === 'ok')
          setBusy(!!h?.busy)
        }
      } catch {
        if (!cancelled) {
          setBackendOnline(false)
          setBusy(false)
        }
      }
    }
    tick()
    const id = window.setInterval(tick, 4000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [])

  const content = useMemo(() => {
    switch (page) {
      case 'config':
        return <ConfigPage />
      case 'task':
        return <TaskPage />
      case 'ai':
        return <AiPage />
      default:
        return <DashboardPage onNavigate={setPage} />
    }
  }, [page])

  return (
    <Layout className="app-shell">
      <Sider breakpoint="lg" collapsedWidth={64} width={220}>
        <div className="logo">
          <div className="logo-mark">🎟</div>
          <span>DamaiHelper</span>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[page]}
          onClick={({ key }) => setPage(key as PageKey)}
          items={[
            { key: 'dashboard', icon: <DashboardOutlined />, label: '总览' },
            { key: 'config', icon: <SettingOutlined />, label: '配置中心' },
            { key: 'task', icon: <RocketOutlined />, label: '任务编排' },
            { key: 'ai', icon: <ExperimentOutlined />, label: 'YOLO / CUDA' },
          ]}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: colorBgContainer,
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Typography.Title level={4} style={{ margin: 0 }}>
            控制台
          </Typography.Title>
          <Space>
            <Tag icon={<CloudServerOutlined />} color={backendOnline ? 'success' : 'default'}>
              {backendOnline === null ? '检测中' : backendOnline ? '后端在线' : '后端离线'}
            </Tag>
            <Badge status={busy ? 'processing' : 'default'} text={busy ? '任务运行中' : '空闲'} />
          </Space>
        </Header>
        <Content className="content-wrap">
          <div
            style={{
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
              padding: 20,
              minHeight: 480,
            }}
          >
            {content}
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}
