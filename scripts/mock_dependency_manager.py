"""Mock dependency manager used for playful GUI simulations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, List


DEFAULT_DEPENDENCIES = [
    "undetected-chromedriver==2.0",
    "aiohttp>=3.8",
    "httpx>=0.25",
    "scikit-learn",
    "onnxruntime",
    "prometheus-client",
    "grafana-api",
    "celery",
    "redis",
    "pymongo",
    "ray",
    "uvloop",
    "orjson",
]


@dataclass(frozen=True)
class MockInstallStep:
    dependency: str
    detail: str


def default_dependencies() -> List[str]:
    return list(DEFAULT_DEPENDENCIES)


def build_mock_steps(dependencies: Iterable[str]) -> List[MockInstallStep]:
    steps: List[MockInstallStep] = []
    for dep in dependencies:
        steps.extend(
            [
                MockInstallStep(dep, "解析依赖元数据"),
                MockInstallStep(dep, "下载分布式缓存包"),
                MockInstallStep(dep, "校验哈希与签名"),
                MockInstallStep(dep, "构建本地wheel"),
                MockInstallStep(dep, "完成安装并缓存"),
            ]
        )
    return steps


def build_report(dependencies: Iterable[str]) -> str:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    deps = list(dependencies)
    lines = [
        "TicketMaster Pro - 依赖模拟安装报告",
        f"生成时间: {timestamp}",
        f"依赖数量: {len(deps)}",
        "",
    ]
    for step in build_mock_steps(deps):
        lines.append(f"[{step.dependency}] {step.detail}")
    lines.append("")
    lines.append("说明: 以上为模拟输出，并未执行真实安装。")
    return "\n".join(lines)
