# coding: utf-8
"""Appium 移动端模拟（默认 dry-run，不连接真机）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


DEFAULT_CAPS: Dict[str, Any] = {
    "platformName": "Android",
    "deviceName": "device",
    "appPackage": "com.damai.android",
    "appActivity": ".activity.MainActivity",
}


@dataclass
class AppiumSession:
    account_info: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True
    caps: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_CAPS))
    server_url: str = "http://localhost:4723/wd/hub"
    alive: bool = False
    _driver: Any = None

    def start(self) -> "AppiumSession":
        self.alive = True
        if self.dry_run:
            return self
        try:
            from appium import webdriver
        except ImportError as exc:
            raise RuntimeError("未安装 appium-python-client") from exc
        self._driver = webdriver.Remote(self.server_url, self.caps)
        return self

    def tap_login(self) -> None:
        if self.dry_run:
            return
        if not self._driver:
            raise RuntimeError("Appium 会话未启动")
        # 兼容旧 API 命名；真机环境按实际控件调整
        try:
            self._driver.find_element("id", "com.damai.android:id/login_button").click()
        except Exception:
            pass

    def quit(self) -> None:
        self.alive = False
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None


def start_simulation(
    account_info: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
    server_url: str = "http://localhost:4723/wd/hub",
) -> AppiumSession:
    """启动 Appium 模拟会话并执行基础登录点击。"""
    session = AppiumSession(
        account_info=account_info or {},
        dry_run=dry_run,
        server_url=server_url,
    )
    session.start()
    try:
        session.tap_login()
    finally:
        if dry_run:
            session.quit()
    return session
