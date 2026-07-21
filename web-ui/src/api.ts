import axios from 'axios'

/** 开发时走 Vite 代理；生产与后端同域 */
const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export type TaskStatus = 'idle' | 'running' | 'completed' | 'stopped' | 'error'

export interface LogEntry {
  ts?: string
  level: string
  message: string
}

export interface TaskSnapshot {
  status: TaskStatus | string
  progress: number
  logs: LogEntry[]
  task_type?: string
  task_id?: string
  message?: string
  total_logs?: number
  offset?: number
  busy?: boolean
}

export async function getHealth() {
  const { data } = await api.get('/health')
  return data
}

export async function getConfig() {
  const { data } = await api.get('/config')
  return data
}

export async function saveConfig(config: unknown) {
  const { data } = await api.post('/config', config)
  return data
}

export async function startTicket(payload: Record<string, unknown> = { dry_run: true }) {
  const { data } = await api.post('/ticket/start', payload)
  return data
}

export async function stopTicket() {
  const { data } = await api.post('/ticket/stop')
  return data
}

export async function getTicketLogs(offset = 0): Promise<TaskSnapshot> {
  const { data } = await api.get('/ticket/logs', { params: { offset } })
  return data
}

export async function installDependencies(packages: string[]) {
  const { data } = await api.post('/dependencies/install', { packages })
  return data
}

export async function getAiStatus() {
  const { data } = await api.get('/ai/status')
  return data
}

export async function loadAi(payload: { allow_download?: boolean; device?: string } = {}) {
  const { data } = await api.post('/ai/load', payload)
  return data
}

export async function runSlider(image?: string) {
  const { data } = await api.post('/ai/slider', image ? { image } : {})
  return data
}

export async function runDetect(image?: string) {
  const { data } = await api.post('/ai/detect', image ? { image } : {})
  return data
}

export default api
