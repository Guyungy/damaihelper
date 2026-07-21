# coding: utf-8
"""CLI 入口：加载配置并调度抢票逻辑。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 保证以脚本方式运行时可找到包内模块
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.config_manager import load_config, resolve_ticket_params  # noqa: E402
from scripts.multi_account_manager import manage_multiple_accounts  # noqa: E402
from scripts.scheduler import schedule_tasks  # noqa: E402
from scripts.task_runner import TaskRunner  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DamaiHelper 逻辑层 CLI")
    parser.add_argument("--config", default=None, help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", default=True, help="仅跑逻辑，不启动真浏览器")
    parser.add_argument("--real", action="store_true", help="关闭 dry-run（仍不保证能真实抢票）")
    parser.add_argument("--schedule", action="store_true", help="仅注册定时任务并打印计划")
    parser.add_argument("--accounts", action="store_true", help="执行多账户逻辑流程")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    params = resolve_ticket_params(config)
    dry_run = not args.real

    print("=== DamaiHelper CLI ===")
    print(f"platform={params['platform']} event={params['event_url']}")
    print(f"tickets={params['tickets']} auto_strike={params['auto_strike']} dry_run={dry_run}")

    if args.schedule:
        strike = params.get("strike_time") or ""
        auto_time = "00:00"
        if "T" in strike:
            auto_time = strike.split("T", 1)[1][:5]
        sched = schedule_tasks(
            retry_interval=3,
            auto_buy_time=auto_time,
            strike_time=strike,
            start=False,
        )
        print("scheduled jobs:", sched.plan_summary())
        return 0

    if args.accounts:
        results = manage_multiple_accounts(
            config.get("accounts") or {},
            ticket_settings={
                "tickets": params["tickets"],
                "viewers": params["viewers"],
            },
            dry_run=dry_run,
        )
        print("account results:", results)
        return 0

    # 默认：跑一次完整编排（与 Web 后端同一套 TaskRunner）
    runner = TaskRunner()
    result = runner.start_ticket(config=config, dry_run=dry_run)
    print("start:", result)
    if result.get("status") != "started":
        return 1

    # 简单阻塞等待完成
    import time

    while True:
        snap = runner.get_status()
        if snap["status"] in ("completed", "stopped", "error", "idle"):
            print("final status:", snap["status"], "progress:", snap["progress"])
            for log in snap["logs"][-5:]:
                print(f"  [{log['level']}] {log['message']}")
            break
        time.sleep(0.2)
    return 0 if runner.get_status()["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
