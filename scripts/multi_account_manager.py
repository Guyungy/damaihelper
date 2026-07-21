# coding: utf-8
"""多账户调度逻辑。"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .selenium_driver import DriverSession, start_selenium_driver

LogFn = Callable[[str, str], None]


def _noop_log(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def manage_account(
    account_id: str,
    account_info: Dict[str, Any],
    ticket_settings: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
    log: Optional[LogFn] = None,
) -> Dict[str, Any]:
    """为单个账户执行登录 + 打开目标页的逻辑流程。"""
    log = log or _noop_log
    ticket_settings = ticket_settings or {}
    target = account_info.get("target") or {}
    credentials = account_info.get("credentials") or {}
    target_url = target.get("event_url") or account_info.get("target_url") or ""
    platform = account_info.get("platform") or "damai"
    mobile = credentials.get("mobile") or account_info.get("username") or ""

    log("INFO", f"[{account_id}] 平台={platform} 开始处理")
    if not target_url:
        log("WARNING", f"[{account_id}] 未配置 event_url，跳过")
        return {"account_id": account_id, "status": "skipped", "reason": "missing_event_url"}

    session: DriverSession = start_selenium_driver(target_url, dry_run=dry_run)
    try:
        log("INFO", f"[{account_id}] 浏览器会话已建立 (dry_run={dry_run})")
        if mobile:
            log("DEBUG", f"[{account_id}] 使用账号标识: {mobile}")
        # 登录逻辑占位：真实环境中在此输入账密 / 注入 cookie
        log("INFO", f"[{account_id}] 登录流程完成（逻辑层）")
        session.get(target_url)
        log("INFO", f"[{account_id}] 已打开目标页: {target_url}")

        tickets = int(target.get("tickets") or ticket_settings.get("tickets") or 1)
        viewers = target.get("viewers") or ticket_settings.get("viewers") or [0]
        log("INFO", f"[{account_id}] 计划购票 {tickets} 张，观演人索引 {viewers}")

        return {
            "account_id": account_id,
            "status": "ok",
            "platform": platform,
            "target_url": target_url,
            "tickets": tickets,
            "viewers": viewers,
            "dry_run": dry_run,
        }
    finally:
        session.quit()
        log("DEBUG", f"[{account_id}] 浏览器会话已关闭")


def manage_multiple_accounts(
    accounts: Dict[str, Dict[str, Any]],
    ticket_settings: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
    log: Optional[LogFn] = None,
) -> List[Dict[str, Any]]:
    """顺序处理多个账户，返回每个账户的结果摘要。"""
    log = log or _noop_log
    results: List[Dict[str, Any]] = []
    if not accounts:
        log("WARNING", "账户列表为空")
        return results

    log("SYSTEM", f"多账户调度启动，共 {len(accounts)} 个账户")
    for account_id, info in accounts.items():
        result = manage_account(
            account_id,
            info or {},
            ticket_settings=ticket_settings,
            dry_run=dry_run,
            log=log,
        )
        results.append(result)
    log("SYSTEM", f"多账户调度结束，成功 {sum(1 for r in results if r.get('status') == 'ok')} 个")
    return results
