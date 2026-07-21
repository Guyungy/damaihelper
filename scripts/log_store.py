# coding: utf-8
"""线程安全的任务状态与日志缓冲。"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional


class LogStore:
    """进程内共享的任务状态与日志队列。"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.status: str = "idle"  # idle | running | completed | stopped | error
        self.progress: int = 0
        self.task_type: str = ""  # ticket | dependency | ""
        self.task_id: str = ""
        self.message: str = ""
        self.logs: List[Dict[str, Any]] = []
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None

    def reset(self, task_type: str = "", task_id: str = "") -> None:
        with self._lock:
            self.status = "running"
            self.progress = 0
            self.task_type = task_type
            self.task_id = task_id
            self.message = ""
            self.logs = []
            self.started_at = time.time()
            self.finished_at = None

    def add_log(self, level: str, message: str, **extra: Any) -> Dict[str, Any]:
        entry = {
            "ts": time.strftime("%H:%M:%S"),
            "level": (level or "INFO").upper(),
            "message": message,
        }
        if extra:
            entry.update(extra)
        with self._lock:
            self.logs.append(entry)
        return entry

    def set_progress(self, progress: int, message: Optional[str] = None) -> None:
        with self._lock:
            self.progress = max(0, min(100, int(progress)))
            if message is not None:
                self.message = message

    def set_status(self, status: str, message: Optional[str] = None, progress: Optional[int] = None) -> None:
        with self._lock:
            self.status = status
            if message is not None:
                self.message = message
            if progress is not None:
                self.progress = max(0, min(100, int(progress)))
            if status in ("completed", "stopped", "error", "idle"):
                self.finished_at = time.time()

    def snapshot(self, offset: int = 0) -> Dict[str, Any]:
        with self._lock:
            safe_offset = max(0, min(offset, len(self.logs)))
            return {
                "status": self.status,
                "progress": self.progress,
                "task_type": self.task_type,
                "task_id": self.task_id,
                "message": self.message,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "total_logs": len(self.logs),
                "offset": safe_offset,
                "logs": list(self.logs[safe_offset:]),
            }


# 全局单例，供 web_server 与 runner 共享
store = LogStore()
