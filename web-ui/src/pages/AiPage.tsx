import { useEffect, useState } from 'react'
import {
  Typography,
  Card,
  Button,
  Space,
  Descriptions,
  Tag,
  App,
  Row,
  Col,
  Statistic,
  Alert,
  Switch,
  Input,
} from 'antd'
import { ReloadOutlined, CloudDownloadOutlined, AimOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { getAiStatus, loadAi, runDetect, runSlider } from '../api'

export default function AiPage() {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [allowDownload, setAllowDownload] = useState(false)
  const [lastResult, setLastResult] = useState<any>(null)
  const [imageB64, setImageB64] = useState('')

  const refresh = async () => {
    setLoading(true)
    try {
      const res = await getAiStatus()
      setData(res)
    } catch (e: any) {
      message.error(e?.message || '获取 AI 状态失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const onLoad = async () => {
    setLoading(true)
    try {
      const res = await loadAi({ allow_download: allowDownload })
      setData((prev: any) => ({ ...prev, engine: res.engine }))
      message.success(res.engine?.mock_mode ? '已进入 Mock 模式' : '模型已加载')
      await refresh()
    } catch (e: any) {
      message.error(e?.response?.data?.message || e?.message || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const onSlider = async () => {
    setLoading(true)
    try {
      const res = await runSlider(imageB64 || undefined)
      setLastResult(res)
      message.success(res.message || `offset=${res.offset_px}`)
    } catch (e: any) {
      message.error(e?.message || '滑块求解失败')
    } finally {
      setLoading(false)
    }
  }

  const onDetect = async () => {
    setLoading(true)
    try {
      const res = await runDetect(imageB64 || undefined)
      setLastResult(res)
      message.success(`检测到 ${res.count ?? 0} 个目标`)
    } catch (e: any) {
      message.error(e?.message || '检测失败')
    } finally {
      setLoading(false)
    }
  }

  const env = data?.environment || {}
  const engine = data?.engine || {}
  const torch = env.torch || {}
  const gpu = env.gpu || {}

  return (
    <>
      <Typography.Title level={3} className="page-title">
        YOLO / CUDA
      </Typography.Title>

      {!torch.installed && (
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          message="尚未安装 PyTorch / YOLO"
          description={
            <span>
              在项目根目录执行：
              <Typography.Text code>python tools/install_deps.py</Typography.Text>
              （会按本机 NVIDIA 驱动自动尝试 cu128/cu126 轮子）
            </span>
          }
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card loading={loading}>
            <Statistic
              title="CUDA 可用"
              value={torch.cuda_available ? 'Yes' : 'No'}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: torch.cuda_available ? '#1677ff' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card loading={loading}>
            <Statistic title="推荐设备" value={env.recommend_device || '-'} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card loading={loading}>
            <Statistic
              title="引擎模式"
              value={engine.engine_loaded ? 'YOLO' : engine.mock_mode ? 'Mock' : '未加载'}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="环境详情"
        style={{ marginTop: 16 }}
        extra={
          <Button icon={<ReloadOutlined />} onClick={refresh} loading={loading}>
            刷新
          </Button>
        }
      >
        <Descriptions column={{ xs: 1, md: 2 }} size="small">
          <Descriptions.Item label="GPU">{gpu.name || '—'}</Descriptions.Item>
          <Descriptions.Item label="驱动">{gpu.driver || '—'}</Descriptions.Item>
          <Descriptions.Item label="显存">
            {gpu.memory_total_mb ? `${gpu.memory_used_mb ?? '?'} / ${gpu.memory_total_mb} MB` : '—'}
          </Descriptions.Item>
          <Descriptions.Item label="PyTorch">
            {torch.installed ? (
              <Space>
                <Tag color="blue">{torch.version}</Tag>
                <span>cuda={String(torch.cuda_available)}</span>
              </Space>
            ) : (
              '未安装'
            )}
          </Descriptions.Item>
          <Descriptions.Item label="ultralytics">
            {env.ultralytics?.installed ? env.ultralytics.version : '未安装'}
          </Descriptions.Item>
          <Descriptions.Item label="OpenCV">
            {env.opencv?.installed ? env.opencv.version : '未安装'}
          </Descriptions.Item>
          <Descriptions.Item label="权重">{engine.weights || '—'}</Descriptions.Item>
          <Descriptions.Item label="权重存在">
            {engine.weights_exists ? <Tag color="success">是</Tag> : <Tag>否</Tag>}
          </Descriptions.Item>
          <Descriptions.Item label="说明" span={2}>
            {env.message || engine.load_error || '—'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="模型操作" style={{ marginTop: 16 }}>
        <Space wrap style={{ marginBottom: 12 }}>
          <span>允许下载 yolov8n.pt</span>
          <Switch checked={allowDownload} onChange={setAllowDownload} />
          <Button type="primary" icon={<CloudDownloadOutlined />} onClick={onLoad} loading={loading}>
            加载引擎
          </Button>
          <Button icon={<AimOutlined />} onClick={onSlider} loading={loading}>
            滑块求解
          </Button>
          <Button onClick={onDetect} loading={loading}>
            通用检测
          </Button>
        </Space>
        <Input.TextArea
          rows={3}
          placeholder="可选：粘贴 base64 / dataURL 图片；留空则使用 mock 输入"
          value={imageB64}
          onChange={(e) => setImageB64(e.target.value)}
        />
        {lastResult && (
          <pre
            style={{
              marginTop: 12,
              background: '#fafafa',
              borderRadius: 8,
              padding: 12,
              maxHeight: 280,
              overflow: 'auto',
              fontSize: 12,
            }}
          >
            {JSON.stringify(lastResult, null, 2)}
          </pre>
        )}
      </Card>
    </>
  )
}
