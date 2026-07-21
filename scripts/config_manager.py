# coding: utf-8
"""配置读写、校验与账户解析。"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEMO_CONFIG_PATH = CONFIG_DIR / "demo_config.json"


DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "5.0",
    "global": {
        "log_level": "INFO",
        "timezone": "Asia/Shanghai",
        "ntp_servers": ["time.google.com", "ntp.aliyun.com"],
        "dashboard": {
            "enable": True,
            "host": "0.0.0.0",
            "port": 8765,
        },
    },
    "accounts": {},
    "strategy": {
        "auto_strike": True,
        "strike_time": "",
        "preheat_stages": [5, 2, 0.5],
        "ai_enabled": False,
        "ai_model_path": "",
        "max_retries": 180,
        "retry_backoff": "exponential",
    },
    "monitor": {
        "enable": False,
        "poll_interval": "1.5s",
        "triggers": [],
    },
    "notification": {"channels": []},
    "plugins": {"custom": []},
    "dependencies": {
        "auto_install": False,
        "packages": [],
    },
}


class ConfigError(Exception):
    """配置相关错误。"""


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config(path: Optional[os.PathLike] = None) -> Dict[str, Any]:
    """按优先级加载配置：指定路径 > config.json > demo_config.json > 默认值。"""
    candidates: List[Path] = []
    if path is not None:
        candidates.append(Path(path))
    candidates.extend([CONFIG_PATH, DEMO_CONFIG_PATH])

    for candidate in candidates:
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return _deep_merge(DEFAULT_CONFIG, raw if isinstance(raw, dict) else {})
    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(config: Dict[str, Any], path: Optional[os.PathLike] = None) -> Path:
    ensure_config_dir()
    target = Path(path) if path is not None else CONFIG_PATH
    validated = validate_config(config)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)
    return target


def validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise ConfigError("配置必须是 JSON 对象")

    merged = _deep_merge(DEFAULT_CONFIG, config)

    dashboard = merged.get("global", {}).get("dashboard", {})
    port = dashboard.get("port", 8765)
    try:
        port = int(port)
    except (TypeError, ValueError) as exc:
        raise ConfigError("dashboard.port 必须是整数") from exc
    if not (1 <= port <= 65535):
        raise ConfigError("dashboard.port 必须在 1-65535 之间")
    merged["global"]["dashboard"]["port"] = port

    strategy = merged.get("strategy", {})
    max_retries = strategy.get("max_retries", 180)
    try:
        strategy["max_retries"] = max(0, int(max_retries))
    except (TypeError, ValueError) as exc:
        raise ConfigError("strategy.max_retries 必须是整数") from exc
    merged["strategy"] = strategy

    accounts = merged.get("accounts")
    if accounts is None:
        merged["accounts"] = {}
    elif not isinstance(accounts, dict):
        raise ConfigError("accounts 必须是对象")

    return merged


def list_accounts(config: Optional[Dict[str, Any]] = None) -> List[str]:
    cfg = config if config is not None else load_config()
    return list((cfg.get("accounts") or {}).keys())


def get_primary_account(config: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
    """返回第一个账户及其配置；无账户时返回空结构。"""
    cfg = config if config is not None else load_config()
    accounts = cfg.get("accounts") or {}
    if not accounts:
        return "default", {
            "platform": "damai",
            "credentials": {},
            "target": {
                "event_url": "",
                "priorities": {"date": [1], "session": [1], "price_range": "lowest_to_highest"},
                "tickets": 1,
                "viewers": [0],
            },
            "proxy": {},
        }
    account_id = next(iter(accounts))
    return account_id, accounts[account_id] or {}


def resolve_ticket_params(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """将新版 config 结构解析为抢票编排器可直接使用的扁平参数。"""
    cfg = config if config is not None else load_config()
    account_id, account = get_primary_account(cfg)
    target = account.get("target") or {}
    credentials = account.get("credentials") or {}
    priorities = target.get("priorities") or {}
    strategy = cfg.get("strategy") or {}
    proxy = account.get("proxy") or {}

    return {
        "account_id": account_id,
        "platform": account.get("platform") or "damai",
        "mobile": credentials.get("mobile") or "",
        "event_url": target.get("event_url") or "",
        "date_priorities": priorities.get("date") or [1],
        "session_priorities": priorities.get("session") or [1],
        "price_range": priorities.get("price_range") or "lowest_to_highest",
        "tickets": int(target.get("tickets") or 1),
        "viewers": target.get("viewers") or [0],
        "proxy_type": proxy.get("type") or "direct",
        "proxy_addr": proxy.get("addr") or "",
        "auto_strike": bool(strategy.get("auto_strike", True)),
        "strike_time": strategy.get("strike_time") or "",
        "max_retries": int(strategy.get("max_retries") or 180),
        "retry_backoff": strategy.get("retry_backoff") or "exponential",
        "ai_enabled": bool(strategy.get("ai_enabled", False)),
        "preheat_stages": strategy.get("preheat_stages") or [5, 2, 0.5],
        "log_level": (cfg.get("global") or {}).get("log_level") or "INFO",
        "timezone": (cfg.get("global") or {}).get("timezone") or "Asia/Shanghai",
    }
