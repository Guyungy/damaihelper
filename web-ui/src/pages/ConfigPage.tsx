import { useEffect, useState } from 'react'
import {
  Typography,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  App,
  Card,
  Row,
  Col,
  Select,
  Divider,
} from 'antd'
import { SaveOutlined, ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import { getConfig, saveConfig } from '../api'

function flattenForForm(cfg: any) {
  const acc = cfg?.accounts?.acc_primary || Object.values(cfg?.accounts || {})[0] || {}
  const target = acc.target || {}
  const cred = acc.credentials || {}
  const proxy = acc.proxy || {}
  const strategy = cfg?.strategy || {}
  const dash = cfg?.global?.dashboard || {}
  const deps = cfg?.dependencies || {}

  return {
    log_level: cfg?.global?.log_level || 'INFO',
    timezone: cfg?.global?.timezone || 'Asia/Shanghai',
    dashboard_enable: dash.enable !== false,
    dashboard_host: dash.host || '0.0.0.0',
    dashboard_port: dash.port || 8765,
    platform: acc.platform || 'damai',
    mobile: cred.mobile || '',
    password: cred.password || '',
    event_url: target.event_url || '',
    date_priorities: (target.priorities?.date || [1]).join(','),
    session_priorities: (target.priorities?.session || [1]).join(','),
    tickets: target.tickets || 1,
    viewers: (target.viewers || [0]).join(','),
    proxy_type: proxy.type || 'direct',
    proxy_addr: proxy.addr || '',
    auto_strike: strategy.auto_strike !== false,
    strike_time: strategy.strike_time || '',
    ai_enabled: !!strategy.ai_enabled,
    max_retries: strategy.max_retries || 180,
    auto_install: !!deps.auto_install,
    packages: (deps.packages || []).join('\n'),
    _raw: cfg,
  }
}

function buildConfigFromForm(values: any, prev: any) {
  const parseList = (s: string) =>
    String(s || '')
      .split(/[,\s]+/)
      .map((x) => x.trim())
      .filter(Boolean)
      .map((x) => (Number.isNaN(Number(x)) ? x : Number(x)))

  const packages = String(values.packages || '')
    .split('\n')
    .map((s: string) => s.trim())
    .filter(Boolean)

  const base = prev && typeof prev === 'object' ? structuredClone(prev) : {}
  base.version = base.version || '5.0'
  base.global = {
    ...(base.global || {}),
    log_level: values.log_level,
    timezone: values.timezone,
    dashboard: {
      enable: values.dashboard_enable,
      host: values.dashboard_host,
      port: values.dashboard_port,
    },
  }
  base.accounts = base.accounts || {}
  const accId = Object.keys(base.accounts)[0] || 'acc_primary'
  base.accounts[accId] = {
    ...(base.accounts[accId] || {}),
    platform: values.platform,
    credentials: {
      ...((base.accounts[accId] || {}).credentials || {}),
      mobile: values.mobile,
      password: values.password,
    },
    target: {
      event_url: values.event_url,
      priorities: {
        date: parseList(values.date_priorities),
        session: parseList(values.session_priorities),
        price_range: (base.accounts[accId]?.target?.priorities?.price_range) || 'lowest_to_highest',
      },
      tickets: values.tickets,
      viewers: parseList(values.viewers),
    },
    proxy: {
      type: values.proxy_type,
      addr: values.proxy_addr,
      rotate_interval: base.accounts[accId]?.proxy?.rotate_interval || '300s',
    },
  }
  base.strategy = {
    ...(base.strategy || {}),
    auto_strike: values.auto_strike,
    strike_time: values.strike_time,
    ai_enabled: values.ai_enabled,
    max_retries: values.max_retries,
  }
  base.dependencies = {
    ...(base.dependencies || {}),
    auto_install: values.auto_install,
    packages,
  }
  return base
}

export default function ConfigPage() {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [raw, setRaw] = useState<any>(null)

  const load = async () => {
    setLoading(true)
    try {
      const cfg = await getConfig()
      setRaw(cfg)
      form.setFieldsValue(flattenForForm(cfg))
      message.success('配置已加载')
    } catch (e: any) {
      message.error(e?.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const onSave = async () => {
    try {
      const values = await form.validateFields()
      const cfg = buildConfigFromForm(values, raw)
      setLoading(true)
      const res = await saveConfig(cfg)
      setRaw(cfg)
      message.success(res?.message || '已保存到后端')
    } catch (e: any) {
      if (e?.errorFields) return
      message.error(e?.response?.data?.message || e?.message || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  const onDownload = async () => {
    const values = form.getFieldsValue(true)
    const cfg = buildConfigFromForm(values, raw)
    const blob = new Blob([JSON.stringify(cfg, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'config.json'
    a.click()
    URL.revokeObjectURL(url)
    message.success('已导出 config.json')
  }

  return (
    <>
      <Typography.Title level={3} className="page-title">
        配置中心
      </Typography.Title>
      <Form form={form} layout="vertical" disabled={loading}>
        <Card title="面板 / 全局" size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="log_level" label="日志级别">
                <Select
                  options={['DEBUG', 'INFO', 'WARNING', 'ERROR'].map((v) => ({ value: v, label: v }))}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="timezone" label="时区">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="dashboard_port" label="端口">
                <InputNumber style={{ width: '100%' }} min={1} max={65535} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="dashboard_host" label="监听地址">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="dashboard_enable" label="启用面板" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card title="账户 / 目标" size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="platform" label="平台">
                <Select
                  options={[
                    { value: 'damai', label: '大麦' },
                    { value: 'taopiaopiao', label: '淘票票' },
                    { value: 'binwandao', label: '缤玩岛' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="mobile" label="手机号">
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="password" label="密码">
                <Input.Password />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Form.Item
                name="event_url"
                label="演出链接"
                rules={[{ required: true, message: '请填写演出链接' }]}
              >
                <Input placeholder="https://detail.damai.cn/item.htm?id=..." />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="date_priorities" label="日期优先级">
                <Input placeholder="1,2" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="session_priorities" label="场次优先级">
                <Input placeholder="1" />
              </Form.Item>
            </Col>
            <Col xs={24} md={4}>
              <Form.Item name="tickets" label="票数">
                <InputNumber min={1} max={6} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={4}>
              <Form.Item name="viewers" label="观演人索引">
                <Input placeholder="0,1" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Card title="策略 / 代理 / 依赖" size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item name="auto_strike" label="自动下单" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="ai_enabled" label="启用 AI / YOLO" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item name="max_retries" label="最大重试">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="strike_time" label="开售时间">
                <Input placeholder="2026-06-30T20:00:00" />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="proxy_type" label="代理类型">
                <Select
                  options={[
                    { value: 'direct', label: '直连' },
                    { value: 'http', label: 'HTTP' },
                    { value: 'socks5', label: 'SOCKS5' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="proxy_addr" label="代理地址">
                <Input placeholder="user:pass@host:port" />
              </Form.Item>
            </Col>
            <Col xs={24}>
              <Divider style={{ margin: '8px 0 16px' }} />
              <Form.Item name="auto_install" label="依赖自动安装" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="packages" label="依赖包列表（每行一个）">
                <Input.TextArea rows={5} placeholder="ultralytics&#10;httpx" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        <Space>
          <Button type="primary" icon={<SaveOutlined />} onClick={onSave} loading={loading}>
            保存到后端
          </Button>
          <Button icon={<ReloadOutlined />} onClick={load}>
            重新加载
          </Button>
          <Button icon={<DownloadOutlined />} onClick={onDownload}>
            导出 JSON
          </Button>
        </Space>
      </Form>
    </>
  )
}
