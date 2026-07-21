# coding: utf-8
"""定时调度封装。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


JobFunc = Callable[[], Any]


@dataclass
class ScheduledJob:
    name: str
    trigger: str  # cron | interval | date
    func: JobFunc
    kwargs: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class TaskScheduler:
    """轻量调度器：有 APScheduler 时用真调度，否则仅登记计划。"""

    def __init__(self) -> None:
        self.jobs: List[ScheduledJob] = []
        self._scheduler = None
        self._started = False

    def add_cron_job(self, func: JobFunc, hour: int, minute: int, name: str = "cron_job") -> ScheduledJob:
        job = ScheduledJob(name=name, trigger="cron", func=func, kwargs={"hour": hour, "minute": minute})
        self.jobs.append(job)
        return job

    def add_interval_job(self, func: JobFunc, seconds: int, name: str = "interval_job") -> ScheduledJob:
        job = ScheduledJob(name=name, trigger="interval", func=func, kwargs={"seconds": max(1, int(seconds))})
        self.jobs.append(job)
        return job

    def add_date_job(self, func: JobFunc, run_date: str, name: str = "date_job") -> ScheduledJob:
        job = ScheduledJob(name=name, trigger="date", func=func, kwargs={"run_date": run_date})
        self.jobs.append(job)
        return job

    def plan_summary(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": j.name,
                "trigger": j.trigger,
                "kwargs": j.kwargs,
                "enabled": j.enabled,
            }
            for j in self.jobs
        ]

    def start(self, blocking: bool = False) -> bool:
        """尝试用 APScheduler 启动；不可用则只标记已登记。"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.schedulers.blocking import BlockingScheduler
        except ImportError:
            self._started = False
            return False

        scheduler = BlockingScheduler() if blocking else BackgroundScheduler()
        for job in self.jobs:
            if not job.enabled:
                continue
            if job.trigger == "cron":
                scheduler.add_job(job.func, "cron", id=job.name, **job.kwargs)
            elif job.trigger == "interval":
                scheduler.add_job(job.func, "interval", id=job.name, **job.kwargs)
            elif job.trigger == "date":
                run_date = job.kwargs.get("run_date")
                scheduler.add_job(job.func, "date", id=job.name, run_date=run_date)

        self._scheduler = scheduler
        if blocking:
            self._started = True
            scheduler.start()
        else:
            scheduler.start()
            self._started = True
        return True

    def shutdown(self) -> None:
        if self._scheduler is not None:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception:
                pass
            self._scheduler = None
        self._started = False


def parse_hhmm(value: str) -> tuple:
    parts = (value or "00:00").split(":")
    hour = int(parts[0]) if parts else 0
    minute = int(parts[1]) if len(parts) > 1 else 0
    return hour % 24, minute % 60


def schedule_tasks(
    retry_interval: int = 3,
    auto_buy_time: str = "00:00",
    buy_func: Optional[JobFunc] = None,
    retry_func: Optional[JobFunc] = None,
    strike_time: str = "",
    start: bool = False,
) -> TaskScheduler:
    """根据配置注册抢票与重试任务，返回调度器实例。"""

    def _default_buy() -> None:
        print(f"[{datetime.now().isoformat()}] 执行抢票任务...")

    def _default_retry() -> None:
        print(f"[{datetime.now().isoformat()}] 重试抢票任务...")

    scheduler = TaskScheduler()
    hour, minute = parse_hhmm(auto_buy_time)
    scheduler.add_cron_job(buy_func or _default_buy, hour=hour, minute=minute, name="auto_buy")
    scheduler.add_interval_job(retry_func or _default_retry, seconds=retry_interval, name="retry_buy")

    if strike_time:
        scheduler.add_date_job(buy_func or _default_buy, run_date=strike_time, name="strike_once")

    if start:
        scheduler.start(blocking=False)
    return scheduler
