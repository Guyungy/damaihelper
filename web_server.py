# coding: utf-8
"""DamaiHelper Web 控制中心：静态资源 + REST API。

API 契约（web/index.html 与 web-ui Ant Design 共用）：
  GET  /api/config
  POST /api/config
  POST /api/ticket/start
  POST /api/ticket/stop
  GET  /api/ticket/logs?offset=0
  GET  /api/ticket/status?offset=0
  POST /api/dependencies/install
  GET  /api/dependencies/report
  GET  /api/health
  GET  /api/ai/status
  POST /api/ai/load
  POST /api/ai/detect
  POST /api/ai/slider
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse, unquote

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.config_manager import (  # noqa: E402
    ConfigError,
    load_config,
    save_config,
)
from scripts.device_probe import environment_report  # noqa: E402
from scripts.mock_dependency_manager import build_report, default_dependencies  # noqa: E402
from scripts.task_runner import runner  # noqa: E402
from scripts.yolo_engine import engine as yolo_engine  # noqa: E402

PORT = 8765
WEB_UI_DIST = ROOT / "web-ui" / "dist"
LEGACY_WEB = ROOT / "web"


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def _read_json_body(handler: SimpleHTTPRequestHandler) -> Tuple[Optional[Any], Optional[str]]:
    length = int(handler.headers.get("Content-Length", 0) or 0)
    raw = handler.rfile.read(length) if length > 0 else b""
    if not raw:
        return {}, None
    try:
        return json.loads(raw.decode("utf-8")), None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"无效 JSON: {exc}"


class DashboardHTTPRequestHandler(SimpleHTTPRequestHandler):
    """静态站点 + /api/* 路由。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    # ---- CORS / helpers -------------------------------------------------
    def _send_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, status: int, payload: Any) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, status: int, text: str, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    # ---- routing --------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path if parsed.path != "/" else "/"
        # 规范化：去掉末尾斜杠（根路径除外）
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        if path.startswith("/api/"):
            return self._handle_api_get(path, parsed)

        # 优先 Ant Design 构建产物，其次旧版 web/index.html
        if path in ("/", "/dashboard", "/app"):
            if (WEB_UI_DIST / "index.html").exists():
                return self._serve_file(WEB_UI_DIST / "index.html")
            self.path = "/web/index.html"
            return super().do_GET()

        # SPA 静态资源：/assets/* 从 web-ui/dist 提供
        if path.startswith("/assets/") and WEB_UI_DIST.exists():
            candidate = (WEB_UI_DIST / path.lstrip("/")).resolve()
            if str(candidate).startswith(str(WEB_UI_DIST.resolve())) and candidate.is_file():
                return self._serve_file(candidate)

        # 旧版兼容
        if path.startswith("/web/"):
            return super().do_GET()

        # Ant Design SPA fallback（history 路由）
        if (WEB_UI_DIST / "index.html").exists() and not path.startswith("/api"):
            # 尝试 dist 下真实文件
            candidate = (WEB_UI_DIST / unquote(path.lstrip("/"))).resolve()
            if str(candidate).startswith(str(WEB_UI_DIST.resolve())) and candidate.is_file():
                return self._serve_file(candidate)
            return self._serve_file(WEB_UI_DIST / "index.html")

        return super().do_GET()

    def _serve_file(self, file_path: Path) -> None:
        if not file_path.is_file():
            self._json_response(404, {"status": "error", "message": "not found"})
            return
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if not path.startswith("/api/"):
            self._json_response(404, {"status": "error", "message": "not found"})
            return
        self._handle_api_post(path)

    def _handle_api_get(self, path: str, parsed) -> None:
        if path == "/api/health":
            self._json_response(
                200,
                {
                    "status": "ok",
                    "service": "damaihelper-web",
                    "busy": runner.is_busy(),
                    "task": runner.get_status(0),
                },
            )
            return

        if path == "/api/config":
            try:
                cfg = load_config()
                self._json_response(200, cfg)
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        if path in ("/api/ticket/logs", "/api/ticket/status"):
            query = parse_qs(parsed.query)
            try:
                offset = int((query.get("offset") or ["0"])[0])
            except ValueError:
                offset = 0
            snap = runner.get_status(offset)
            # 兼容旧前端字段
            self._json_response(
                200,
                {
                    "status": snap["status"],
                    "progress": snap["progress"],
                    "logs": snap["logs"],
                    "task_type": snap.get("task_type"),
                    "task_id": snap.get("task_id"),
                    "message": snap.get("message"),
                    "total_logs": snap.get("total_logs"),
                    "offset": snap.get("offset"),
                    "busy": snap.get("busy"),
                },
            )
            return

        if path == "/api/dependencies/report":
            try:
                cfg = load_config()
                packages = list((cfg.get("dependencies") or {}).get("packages") or default_dependencies())
                report = build_report(packages)
                self._text_response(200, report)
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        if path == "/api/ai/status":
            try:
                payload = {
                    "status": "ok",
                    "engine": yolo_engine.status(),
                    "environment": environment_report(),
                }
                self._json_response(200, payload)
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        self._json_response(404, {"status": "error", "message": f"unknown endpoint: {path}"})

    def _handle_api_post(self, path: str) -> None:
        body, err = _read_json_body(self)
        if err:
            self._json_response(400, {"status": "error", "message": err})
            return

        if path == "/api/config":
            try:
                if not isinstance(body, dict):
                    raise ConfigError("请求体必须是 JSON 对象")
                target = save_config(body)
                self._json_response(
                    200,
                    {
                        "status": "success",
                        "message": "配置保存成功",
                        "path": str(target),
                    },
                )
            except ConfigError as exc:
                self._json_response(400, {"status": "error", "message": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        if path == "/api/ticket/start":
            # 可选：请求体直接带配置覆盖；否则用磁盘配置
            override = body if isinstance(body, dict) and body else None
            dry_run = True
            if isinstance(body, dict) and "dry_run" in body:
                dry_run = bool(body.get("dry_run"))
                # dry_run 不是配置字段，去掉后再决定是否覆盖配置
                override = {k: v for k, v in body.items() if k != "dry_run"} or None

            if override:
                try:
                    save_config(override)
                    config = load_config()
                except ConfigError as exc:
                    self._json_response(400, {"status": "error", "message": str(exc)})
                    return
            else:
                config = load_config()

            result = runner.start_ticket(config=config, dry_run=dry_run)
            status_code = 200 if result.get("status") == "started" else 409
            if result.get("code") == "missing_event_url":
                status_code = 400
            self._json_response(status_code, result)
            return

        if path == "/api/ticket/stop":
            result = runner.stop()
            self._json_response(200, result)
            return

        if path == "/api/dependencies/install":
            packages = []
            if isinstance(body, dict):
                packages = body.get("packages") or []
            result = runner.start_dependency_install(packages=list(packages))
            status_code = 200 if result.get("status") == "started" else 409
            if result.get("code") == "empty_packages":
                status_code = 400
            self._json_response(status_code, result)
            return

        if path == "/api/ai/load":
            allow_download = True
            device = None
            if isinstance(body, dict):
                allow_download = bool(body.get("allow_download", True))
                device = body.get("device")
            if device:
                yolo_engine.device_pref = str(device)
            try:
                status = yolo_engine.ensure_loaded(allow_download=allow_download)
                self._json_response(200, {"status": "ok", "engine": status})
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        if path == "/api/ai/detect":
            if not isinstance(body, dict):
                self._json_response(400, {"status": "error", "message": "需要 JSON 对象"})
                return
            image = body.get("image")
            conf = body.get("conf")
            try:
                result = yolo_engine.detect(image=image, conf=conf)
                self._json_response(200, {"status": "ok", **result})
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        if path == "/api/ai/slider":
            image = None
            if isinstance(body, dict):
                image = body.get("image")
            try:
                result = yolo_engine.solve_slider(image=image)
                self._json_response(200, {"status": "ok", **result})
            except Exception as exc:  # noqa: BLE001
                self._json_response(500, {"status": "error", "message": str(exc)})
            return

        self._json_response(404, {"status": "error", "message": f"unknown endpoint: {path}"})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # 仅打印 API 访问，避免静态资源刷屏
        try:
            msg = format % args
        except Exception:
            msg = format
        if "/api/" in str(msg):
            sys.stderr.write(
                "%s - - [%s] %s\n"
                % (self.address_string(), self.log_date_time_string(), msg)
            )


def resolve_port() -> int:
    """优先读配置中的 dashboard.port，失败则回退默认。"""
    try:
        cfg = load_config()
        port = int(((cfg.get("global") or {}).get("dashboard") or {}).get("port") or PORT)
        if 1 <= port <= 65535:
            return port
    except Exception:
        pass
    return PORT


def main() -> None:
    os.chdir(ROOT)
    port = resolve_port()

    print("===================================================")
    print("   DamaiHelper Web 控制中心")
    print("===================================================")
    print(f"[*] 工作目录: {ROOT}")
    print(f"[*] 绑定端口: {port}")

    try:
        server = ThreadingHTTPServer(("", port), DashboardHTTPRequestHandler)
    except OSError as exc:
        print(f"\n[!] 无法绑定端口 {port}: {exc}")
        print("[!] 可修改 config/config.json 中 global.dashboard.port，或关闭占用进程。")
        sys.exit(1)

    url = f"http://localhost:{port}/"
    ui = "Ant Design (web-ui/dist)" if (WEB_UI_DIST / "index.html").exists() else "Legacy web/index.html"
    print(f"[+] 服务启动成功: {url}")
    print(f"[+] 前端: {ui}")
    print("[+] API: /api/health /api/config /api/ticket/* /api/dependencies/* /api/ai/*")
    print("---------------------------------------------------")
    print("提示: 保持此窗口运行；Ctrl+C 退出。")
    print("---------------------------------------------------")

    # 延迟打开浏览器，避免阻塞启动日志
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 正在关闭服务...")
        runner.stop()
        server.shutdown()
        print("[*] 已安全退出。")
        sys.exit(0)


if __name__ == "__main__":
    main()
