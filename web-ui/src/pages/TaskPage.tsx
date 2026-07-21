import { useEffect, useRef, useState } from 'react'
import {
  Typography,
  Button,
  Space,
  Progress,
  Tag,
  App,
  Card,
  Row,
  Col,
  Switch,
  Input,
} from 'antd'
import { PlayCircleOutlined, PauseCircleOutlined, ClearOutlined, CloudDownloadOutlined } from '@ant-design/icons'
import {
  getTicketLogs,
  installDependencies,
  startTicket,
  stopTicket,
  type LogEntry,
} from '../api'

const levelColor: Record<string, string> = {
  INFO: 'log-INFO',
  DEBUG: 'log-DEBUG',
  WARNING: 'log-WARNING',
  ERROR: 'log-ERROR',
  SYSTEM: 'log-SYSTEM',
  AI: 'log-AI',
}

export default function TaskPage() {
  const { message } = App.useApp()
  const [running, setRunning] = useState(false)
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [offset, setOffset] = useState(0)
  const [dryRun, setDryRun] = useState(true)
  const [depText, setDepText] = useState('ultralytics\nhttpx\norjson')
  const terminalRef = useRef<HTMLDivElement>(null)
  const pollRef = useRef<number | null>(null)

  const appendLogs = (items: LogEntry[]) => {
    if (!items?.length) return
    setLogs((prev) => [...prev, ...items])
  }

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])

  const stopPolling = () => {
    if (pollRef.current) {
      window.clearTimeout(pollRef.current)
      pollRef.current = null
    }
  }

  const poll = async (nextOffset: number) => {
    try {
      const snap = await getTicketLogs(nextOffset)
      setStatus(snap.status)
      setProgress(snap.progress || 0)
      if (snap.logs?.length) {
        appendLogs(snap.logs)
        nextOffset += snap.logs.length
        setOffset(nextOffset)
      }
      if (['completed', 'stopped', 'error', 'idle'].includes(String(snap.status))) {
        setRunning(false)
        stopPolling()
        return
      }
      pollRef.current = window.setTimeout(() => poll(nextOffset), 400)
    } catch (e: any) {
      message.warning(e?.message || '日志轮询失败')
      pollRef.current = window.setTimeout(() => poll(nextOffset), 1200)
    }
  }

  useEffect(() => () => stopPolling(), [])

  const onStart = async () => {
    try {
      setLogs([])
      setOffset(0)
      setProgress(0)
      setStatus('running')
      setRunning(true)
      const res = await startTicket({ dry_run: dryRun })
      message.success(`任务已启动 ${res.task_id || ''}`)
      poll(0)
    } catch (e: any) {
      setRunning(false)
      setStatus('error')
      message.error(e?.response?.data?.message || e?.message || '启动失败')
    }
  }

  const onStop = async () => {
    try {
      await stopTicket()
      message.info('已发送停止指令')
    } catch (e: any) {
      message.error(e?.message || '停止失败')
    }
  }

  const onDeps = async () => {
    const packages = depText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)
    if (!packages.length) {
      message.warning('依赖列表为空')
      return
    }
    try {
      setLogs([])
      setOffset(0)
      setRunning(true)
      setStatus('running')
      const res = await installDependencies(packages)
      message.success(`依赖任务 ${res.task_id || 'ok'}`)
      poll(0)
    } catch (e: any) {
      setRunning(false)
      message.error(e?.response?.data?.message || e?.message || '依赖安装任务失败')
    }
  }

  return (
    <>
      <Typography.Title level={3} className="page-title">
        任务编排
      </Typography.Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={16}>
          <Card
            title={
              <Space>
                <span>运行控制</span>
                <Tag color={status === 'running' ? 'processing' : status === 'completed' ? 'success' : 'default'}>
                  {status}
                </Tag>
              </Space>
            }
            extra={
              <Space>
                <span className="muted">dry-run</span>
                <Switch checked={dryRun} onChange={setDryRun} />
              </Space>
            }
          >
            <Space wrap style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={onStart}
                disabled={running}
              >
                启动抢票编排
              </Button>
              <Button danger icon={<PauseCircleOutlined />} onClick={onStop} disabled={!running}>
                停止
              </Button>
              <Button
                icon={<ClearOutlined />}
                onClick={() => {
                  setLogs([])
                  setOffset(0)
                }}
              >
                清空日志
              </Button>
            </Space>
            <Progress percent={progress} status={status === 'error' ? 'exception' : running ? 'active' : undefined} />
            <div className="log-terminal" ref={terminalRef} style={{ marginTop: 12 }}>
              {logs.length === 0 && <div className="muted">等待日志...</div>}
              {logs.map((log, idx) => (
                <div className="log-line" key={idx}>
                  <span className="log-time">[{log.ts || '--:--:--'}]</span>
                  <span className={levelColor[log.level] || 'log-INFO'}>[{log.level}] </span>
                  {log.message}
                </div>
              ))}
            </div>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="依赖部署（逻辑任务）">
            <Input.TextArea
              rows={8}
              value={depText}
              onChange={(e) => setDepText(e.target.value)}
              style={{ marginBottom: 12 }}
            />
            <Button
              block
              icon={<CloudDownloadOutlined />}
              onClick={onDeps}
              disabled={running}
            >
              启动依赖任务
            </Button>
            <Typography.Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0 }}>
              真实 pip / CUDA 安装请用：
              <br />
              <Typography.Text code>python tools/install_deps.py</Typography.Text>
            </Typography.Paragraph>
          </Card>
        </Col>
      </Row>
    </>
  )
}
