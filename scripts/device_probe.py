# coding: utf-8
"""本机 CUDA / PyTorch / YOLO 能力探测。"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional


def _nvidia_smi_summary() -> Optional[Dict[str, Any]]:
    smi = shutil.which("nvidia-smi")
    if not smi:
        return None
    try:
        out = subprocess.check_output(
            [
                smi,
                "--query-gpu=name,driver_version,memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        ).strip()
        if not out:
            return None
        line = out.splitlines()[0]
        parts = [p.strip() for p in line.split(",")]
        return {
            "name": parts[0] if parts else "unknown",
            "driver": parts[1] if len(parts) > 1 else "",
            "memory_total_mb": _to_int(parts[2]) if len(parts) > 2 else None,
            "memory_used_mb": _to_int(parts[3]) if len(parts) > 3 else None,
        }
    except Exception:
        return None


def _to_int(value: str) -> Optional[int]:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def probe_torch() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "installed": False,
        "version": None,
        "cuda_available": False,
        "cuda_version": None,
        "device_count": 0,
        "device_name": None,
    }
    try:
        import torch
    except ImportError:
        return info

    info["installed"] = True
    info["version"] = getattr(torch, "__version__", None)
    info["cuda_available"] = bool(torch.cuda.is_available())
    info["cuda_version"] = getattr(torch.version, "cuda", None)
    if info["cuda_available"]:
        info["device_count"] = torch.cuda.device_count()
        try:
            info["device_name"] = torch.cuda.get_device_name(0)
        except Exception:
            info["device_name"] = None
    return info


def probe_ultralytics() -> Dict[str, Any]:
    info: Dict[str, Any] = {"installed": False, "version": None}
    try:
        import ultralytics

        info["installed"] = True
        info["version"] = getattr(ultralytics, "__version__", None)
    except ImportError:
        pass
    return info


def probe_opencv() -> Dict[str, Any]:
    info: Dict[str, Any] = {"installed": False, "version": None}
    try:
        import cv2

        info["installed"] = True
        info["version"] = getattr(cv2, "__version__", None)
    except ImportError:
        pass
    return info


def environment_report() -> Dict[str, Any]:
    """汇总本机 AI 运行环境，供 /api/ai/status 使用。"""
    gpu = _nvidia_smi_summary()
    torch_info = probe_torch()
    yolo_info = probe_ultralytics()
    cv_info = probe_opencv()

    ready = bool(torch_info.get("installed") and yolo_info.get("installed"))
    cuda_ready = bool(torch_info.get("cuda_available"))

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "gpu": gpu,
        "torch": torch_info,
        "ultralytics": yolo_info,
        "opencv": cv_info,
        "ready": ready,
        "cuda_ready": cuda_ready,
        "recommend_device": "cuda:0" if cuda_ready else "cpu",
        "message": _message(ready, cuda_ready, gpu, torch_info, yolo_info),
    }


def _message(ready: bool, cuda_ready: bool, gpu, torch_info, yolo_info) -> str:
    if not torch_info.get("installed"):
        return "未安装 PyTorch，请运行: python tools/install_deps.py"
    if not yolo_info.get("installed"):
        return "未安装 ultralytics，请运行: python tools/install_deps.py"
    if cuda_ready:
        name = (gpu or {}).get("name") or torch_info.get("device_name") or "GPU"
        return f"CUDA 就绪 · {name}"
    if gpu:
        return "检测到 NVIDIA GPU，但当前 torch 未启用 CUDA（可能装了 CPU 轮子）"
    return "AI 模块可用（CPU 模式）"
