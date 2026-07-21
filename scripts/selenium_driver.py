# coding: utf-8
"""Selenium 驱动封装（逻辑层；默认 dry-run 不真正启动浏览器）。"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DriverSession:
    """抽象浏览器会话，便于 dry-run 与真机共用接口。"""

    target_url: str
    dry_run: bool = True
    options: Dict[str, Any] = field(default_factory=dict)
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    current_url: str = ""
    title: str = ""
    alive: bool = False
    _driver: Any = None

    def start(self) -> "DriverSession":
        self.alive = True
        self.current_url = "about:blank"
        self.title = "New Tab"
        if self.dry_run:
            return self

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError as exc:
            raise RuntimeError("未安装 selenium，无法启动真机浏览器") from exc

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if self.options.get("headless"):
            chrome_options.add_argument("--headless=new")
        if self.options.get("mobile_emulation"):
            chrome_options.add_experimental_option(
                "mobileEmulation", {"deviceName": self.options.get("device_name", "Nexus 6")}
            )

        driver_path = self.options.get("driver_path") or _default_driver_path()
        if driver_path and os.path.exists(driver_path):
            self._driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        else:
            # Selenium 4.6+ 可自动管理驱动
            self._driver = webdriver.Chrome(options=chrome_options)
        return self

    def get(self, url: str) -> None:
        self.current_url = url
        self.title = "商品详情" if "detail" in url else url
        if self.dry_run:
            return
        if not self._driver:
            raise RuntimeError("浏览器尚未启动")
        self._driver.get(url)
        self.current_url = self._driver.current_url
        self.title = self._driver.title

    def add_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        self.cookies = list(cookies or [])
        if self.dry_run or not self._driver:
            return
        for cookie in self.cookies:
            try:
                self._driver.add_cookie(cookie)
            except Exception:
                continue

    def quit(self) -> None:
        self.alive = False
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None


def _default_driver_path() -> str:
    name = "chromedriver.exe" if sys.platform.startswith("win") else "chromedriver"
    return os.path.abspath(name)


def build_stealth_options(
    headless: bool = False,
    mobile: bool = True,
    driver_path: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "headless": headless,
        "mobile_emulation": mobile,
        "device_name": "Nexus 6",
        "driver_path": driver_path or _default_driver_path(),
        "stealth": True,
        "page_load_strategy": "eager",
    }


def start_selenium_driver(
    target_url: str,
    dry_run: bool = True,
    headless: bool = False,
    driver_path: Optional[str] = None,
) -> DriverSession:
    """启动浏览器会话并打开目标页。

    dry_run=True 时不真正启动 Chrome，仅维护逻辑状态，供 Web/任务编排使用。
    """
    session = DriverSession(
        target_url=target_url,
        dry_run=dry_run,
        options=build_stealth_options(headless=headless, driver_path=driver_path),
    )
    session.start()
    if target_url:
        session.get(target_url)
    return session
