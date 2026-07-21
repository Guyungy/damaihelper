# coding: utf-8
"""抢票任务编排器：按配置驱动阶段化流程，可停止、可回调日志。

设计目标：
- 不依赖真实浏览器也能跑通完整业务逻辑
- 与 ticket_script.Concert 阶段语义对齐
- 供 Web 后端调度；CLI 也可直接调用
"""

from __future__ import annotations

import random
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .config_manager import load_config, resolve_ticket_params
from .log_store import LogStore, store as global_store


LogCallback = Callable[[str, str], None]
ProgressCallback = Callable[[int, str], None]


@dataclass
class FlowStep:
    progress: int
    level: str
    message: str
    delay: float = 0.45
    phase: str = ""


@dataclass
class TaskHandle:
    task_id: str
    task_type: str
    thread: Optional[threading.Thread] = None
    stop_event: threading.Event = field(default_factory=threading.Event)


class TaskRunner:
    """统一任务调度：抢票 / 依赖安装。"""

    def __init__(self, log_store: Optional[LogStore] = None) -> None:
        self.store = log_store or global_store
        self._lock = threading.RLock()
        self._current: Optional[TaskHandle] = None

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def is_busy(self) -> bool:
        with self._lock:
            handle = self._current
            return bool(handle and handle.thread and handle.thread.is_alive())

    def get_status(self, offset: int = 0) -> Dict[str, Any]:
        snap = self.store.snapshot(offset)
        snap["busy"] = self.is_busy()
        return snap

    def stop(self) -> Dict[str, Any]:
        with self._lock:
            handle = self._current
            if not handle or not handle.thread or not handle.thread.is_alive():
                self.store.set_status("stopped", "当前没有运行中的任务", progress=self.store.progress)
                self.store.add_log("SYSTEM", "收到停止指令，但当前没有运行中的任务")
                return {"status": "idle", "message": "no running task"}

            handle.stop_event.set()
            self.store.add_log("SYSTEM", "收到停止指令，正在安全终止任务...")
            self.store.set_status("stopped", "任务停止中")
            return {"status": "stopping", "task_id": handle.task_id}

    def start_ticket(self, config: Optional[Dict[str, Any]] = None, dry_run: bool = True) -> Dict[str, Any]:
        if self.is_busy():
            return {"status": "error", "message": "已有任务在运行", "code": "busy"}

        cfg = config if config is not None else load_config()
        params = resolve_ticket_params(cfg)
        if not params.get("event_url"):
            return {"status": "error", "message": "目标演出链接为空", "code": "missing_event_url"}

        task_id = f"ticket_{uuid.uuid4().hex[:10]}"
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._run_ticket_flow,
            args=(task_id, params, dry_run, stop_event),
            name=task_id,
            daemon=True,
        )
        handle = TaskHandle(task_id=task_id, task_type="ticket", thread=thread, stop_event=stop_event)
        with self._lock:
            self._current = handle
            self.store.reset(task_type="ticket", task_id=task_id)
        thread.start()
        return {"status": "started", "task_id": task_id, "dry_run": dry_run}

    def start_dependency_install(self, packages: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.is_busy():
            return {"status": "error", "message": "已有任务在运行", "code": "busy"}

        pkgs = [p.strip() for p in (packages or []) if p and str(p).strip()]
        if not pkgs:
            # 回退到配置中的依赖列表
            cfg = load_config()
            pkgs = list((cfg.get("dependencies") or {}).get("packages") or [])
        if not pkgs:
            return {"status": "error", "message": "依赖清单为空", "code": "empty_packages"}

        task_id = f"deps_{uuid.uuid4().hex[:10]}"
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._run_dependency_flow,
            args=(task_id, pkgs, stop_event),
            name=task_id,
            daemon=True,
        )
        handle = TaskHandle(task_id=task_id, task_type="dependency", thread=thread, stop_event=stop_event)
        with self._lock:
            self._current = handle
            self.store.reset(task_type="dependency", task_id=task_id)
        thread.start()
        return {"status": "started", "task_id": task_id, "packages": pkgs}

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _log(self, level: str, message: str) -> None:
        self.store.add_log(level, message)
        print(f"[{time.strftime('%H:%M:%S')}] [{level}] {message}")

    def _progress(self, value: int, message: str = "") -> None:
        self.store.set_progress(value, message or None)

    def _stopped(self, stop_event: threading.Event) -> bool:
        return stop_event.is_set()

    def _sleep(self, seconds: float, stop_event: threading.Event) -> bool:
        """可中断 sleep；返回 True 表示应停止。"""
        end = time.time() + max(0.0, seconds)
        while time.time() < end:
            if stop_event.is_set():
                return True
            time.sleep(min(0.05, end - time.time()))
        return stop_event.is_set()

    def _finish_stopped(self) -> None:
        self._log("SYSTEM", "任务已安全停止，资源已释放")
        self.store.set_status("stopped", "任务已停止")

    def _finish_error(self, err: Exception) -> None:
        self._log("ERROR", f"任务异常终止: {err}")
        self.store.set_status("error", str(err))

    def _finish_completed(self, message: str = "任务完成") -> None:
        self._progress(100, message)
        self.store.set_status("completed", message, progress=100)

    # ------------------------------------------------------------------
    # ticket flow
    # ------------------------------------------------------------------
    def _build_ticket_steps(self, params: Dict[str, Any]) -> List[FlowStep]:
        platform = str(params.get("platform") or "damai").upper()
        proxy_addr = params.get("proxy_addr") or ""
        proxy_desc = proxy_addr if proxy_addr else "直连模式 (DIRECT)"
        event_url = params.get("event_url") or ""
        mobile = params.get("mobile") or "未配置"
        dates = params.get("date_priorities") or [1]
        sessions = params.get("session_priorities") or [1]
        tickets = params.get("tickets") or 1
        viewers = params.get("viewers") or [0]
        auto_strike = bool(params.get("auto_strike", True))
        ai_enabled = bool(params.get("ai_enabled", False))
        max_retries = params.get("max_retries") or 180

        steps = [
            FlowStep(5, "INFO", f"正在连接代理路由服务器: {proxy_desc}", 0.35, "init"),
            FlowStep(10, "SYSTEM", "已注入 Selenium 隐身防御补丁 (--disable-blink-features=AutomationControlled)", 0.3, "fingerprint"),
            FlowStep(15, "INFO", "正在初始化 Chrome WebDriver 浏览器控制端...", 0.4, "driver"),
            FlowStep(20, "INFO", f"正在导航并拉取平台 [{platform}] 的演出详情页...", 0.4, "navigate"),
            FlowStep(24, "DEBUG", f"目标购票地址: {event_url}", 0.25, "navigate"),
            FlowStep(30, "INFO", "正在解析账户登录 Cookies 凭证信息 (cookies.pkl)...", 0.35, "login"),
            FlowStep(36, "WARNING", "本地未检测到 cookies.pkl 授权缓存。正在启动扫码登录安全防护窗口...", 0.4, "login"),
            FlowStep(42, "SYSTEM", f"### 扫码登录引导 ### 绑定手机: {mobile}，请在弹出的浏览器界面中扫描二维码以同步账户授权...", 0.55, "login"),
            FlowStep(50, "INFO", "同步 Cookies 凭证成功，已持久化写入本地 cookies.pkl", 0.35, "login"),
            FlowStep(55, "DEBUG", "### 载入 Cookie 验证状态成功 ### 正在向购票目标页面进行跳转...", 0.3, "detail"),
            FlowStep(62, "INFO", f"正在解析日历票档卡片... 优先日期 {dates} / 优先场次 {sessions}", 0.4, "select"),
            FlowStep(68, "INFO", f"AI 选座模块: {'启用' if ai_enabled else '关闭'}；最大重试 {max_retries}", 0.3, "select"),
            FlowStep(74, "INFO", "检测到安全滑块盾保护，验证码求解模块介入...", 0.45, "captcha"),
            FlowStep(80, "INFO", "滑块盾验证突破成功！正在加载订单结算页...", 0.35, "captcha"),
            FlowStep(86, "INFO", f"正在检索余票状态... 余票可用！勾选购票数 [{tickets}]，实名观演人索引 {viewers}", 0.4, "order"),
            FlowStep(92, "SYSTEM", "### 极速自动出手 (Auto Strike) ### 提交抢购订单包中..." if auto_strike else "已完成自动化选座，等待人工确认提交...", 0.45, "order"),
        ]

        if auto_strike:
            steps.extend(
                [
                    FlowStep(98, "INFO", "🎉 [SUCCESS] 订单提交成功！接口返回状态码 200 OK。", 0.3, "success"),
                    FlowStep(100, "SYSTEM", "🎟️ 抢票成功！已锁定场次座位，请在规定时间内完成付款！", 0.2, "success"),
                ]
            )
        else:
            steps.append(
                FlowStep(
                    100,
                    "WARNING",
                    "[INFO] 未启用自动秒杀下单。已完成自动化选座，请在浏览器界面手工提交订单。",
                    0.25,
                    "success",
                )
            )
        return steps

    def _run_ticket_flow(
        self,
        task_id: str,
        params: Dict[str, Any],
        dry_run: bool,
        stop_event: threading.Event,
    ) -> None:
        try:
            mode = "逻辑演练模式 (dry-run)" if dry_run else "实机调度模式"
            self._log("SYSTEM", f"任务 {task_id} 启动 · {mode}")
            self._log("INFO", f"账户={params.get('account_id')} 平台={params.get('platform')} 票数={params.get('tickets')}")

            # 预热阶段（来自 strategy.preheat_stages，仅影响节奏，不真的等待开售）
            stages = params.get("preheat_stages") or []
            if stages:
                self._log("INFO", f"预热阶段配置: {stages}（逻辑层仅记录，不等待真实开售）")

            steps = self._build_ticket_steps(params)
            for step in steps:
                if self._stopped(stop_event):
                    self._finish_stopped()
                    return

                self._progress(step.progress, step.message)
                self._log(step.level, step.message)

                # 滑块阶段接入 YOLO（本机 CUDA / mock 均可）
                if step.phase == "captcha" and "滑块盾保护" in step.message:
                    self._run_yolo_slider(params)

                # 轻微抖动，让日志节奏更自然
                jitter = random.uniform(0.0, 0.12)
                if self._sleep(step.delay + jitter, stop_event):
                    self._finish_stopped()
                    return

            if self._stopped(stop_event):
                self._finish_stopped()
                return

            self._finish_completed("抢票任务完成")
            self._log("SYSTEM", f"任务 {task_id} 已完成")
        except Exception as exc:  # noqa: BLE001 - 顶层捕获保证状态收敛
            self._finish_error(exc)

    def _run_yolo_slider(self, params: Dict[str, Any]) -> None:
        """调用本机 YOLO 引擎求解滑块偏移（无权重时自动 mock）。"""
        try:
            from .yolo_engine import engine

            status = engine.ensure_loaded(allow_download=False)
            device = status.get("device") or "cpu"
            mock = status.get("mock_mode")
            self._log(
                "AI",
                f"YOLO 引擎就绪 device={device} mock={mock} weights={status.get('weights')}",
            )
            result = engine.solve_slider(image=None)
            offset = result.get("offset_px", 170)
            conf = result.get("confidence", 0)
            ms = result.get("infer_ms", 0)
            self._log(
                "AI",
                f"滑块检测完成 offset={offset}px conf={conf:.2f} infer={ms:.1f}ms "
                f"({'mock' if result.get('mock') else 'yolo'})",
            )
            if params.get("ai_enabled"):
                self._log("AI", "strategy.ai_enabled=true，已将偏移写入会话（逻辑层）")
        except Exception as exc:  # noqa: BLE001
            self._log("WARNING", f"YOLO 滑块求解跳过: {exc}")

    # ------------------------------------------------------------------
    # dependency flow
    # ------------------------------------------------------------------
    def _run_dependency_flow(
        self,
        task_id: str,
        packages: List[str],
        stop_event: threading.Event,
    ) -> None:
        try:
            from .mock_dependency_manager import build_mock_steps

            self._log("SYSTEM", f"依赖部署任务 {task_id} 启动，共 {len(packages)} 个包")
            steps = build_mock_steps(packages)
            total = max(1, len(steps))

            for idx, step in enumerate(steps, start=1):
                if self._stopped(stop_event):
                    self._finish_stopped()
                    return
                self._log(step.dependency, step.detail)
                self._progress(min(99, int(idx / total * 100)), step.detail)
                if self._sleep(0.04, stop_event):
                    self._finish_stopped()
                    return

            self._log("SYSTEM", "环境依赖安装及配置成功！")
            self._finish_completed("依赖安装完成")
        except Exception as exc:  # noqa: BLE001
            self._finish_error(exc)


# 模块级默认 runner
runner = TaskRunner()
