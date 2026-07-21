# DamaiHelper 集成与启动

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Ant Design 5 + React 18 + Vite（`web-ui/`） |
| 后端 | Python `web_server.py`（ThreadingHTTPServer + REST） |
| AI | 本机 CUDA + PyTorch + Ultralytics YOLO（`scripts/yolo_engine.py`） |
| 编排 | `scripts/task_runner.py` dry-run 逻辑流 |

旧版 `web/index.html` 仍保留；若存在 `web-ui/dist` 则优先提供 Ant Design 面板。

## 一键安装 / 启动

**Windows**

```bat
win一键运行.bat
```

或分步：

```bat
python tools\install_deps.py
cd web-ui && npm install && npm run build && cd ..
python web_server.py
```

**依赖安装器选项**

```bat
python tools\install_deps.py              rem 核心 + CUDA torch 探测 + YOLO
python tools\install_deps.py --cpu-only   rem 强制 CPU torch
python tools\install_deps.py --with-frontend
python tools\install_deps.py --skip-torch
```

本机实测（RTX 4070 / Driver 610 / Python 3.14）可用索引：

- `https://download.pytorch.org/whl/cu128`
- `https://download.pytorch.org/whl/cu126`

> 注意：`pip install -r requirements.txt` 可能先装上 CPU 版 torch（ultralytics 依赖）。请再跑 `tools/install_deps.py`，它会按 CUDA 索引重装 torch。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET/POST | `/api/config` | 配置读写 |
| POST | `/api/ticket/start` | 启动编排（默认 dry_run） |
| POST | `/api/ticket/stop` | 停止 |
| GET | `/api/ticket/logs?offset=` | 增量日志 |
| POST | `/api/dependencies/install` | 依赖逻辑任务 |
| GET | `/api/ai/status` | GPU / torch / YOLO 环境 |
| POST | `/api/ai/load` | 加载权重（`allow_download`） |
| POST | `/api/ai/detect` | 目标检测 |
| POST | `/api/ai/slider` | 滑块偏移求解 |

## 前端开发

```bat
python web_server.py
cd web-ui
npm run dev
```

Vite 开发服 `http://localhost:5173`，`/api` 代理到 `8765`。

## 目录

```
tools/install_deps.py     一键装依赖
web-ui/                   Ant Design 工程
web-ui/dist/              构建产物（由 web_server 托管）
scripts/yolo_engine.py    YOLO 封装
scripts/device_probe.py   CUDA 探测
models/                   权重目录（yolov8n.pt）
```
