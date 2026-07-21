# coding: utf-8
"""一键安装依赖：核心包 + 本机 CUDA 版 PyTorch + YOLO。

用法:
  python tools/install_deps.py
  python tools/install_deps.py --skip-torch
  python tools/install_deps.py --cpu-only
  python tools/install_deps.py --with-frontend
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
REQ = ROOT / "requirements.txt"
WEB_UI = ROOT / "web-ui"


def run(cmd: Sequence[str], check: bool = True, env: Optional[dict] = None) -> int:
    print(f"\n>>> {' '.join(cmd)}")
    completed = subprocess.run(list(cmd), cwd=str(ROOT), env=env)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def detect_nvidia() -> Tuple[bool, str]:
    """返回 (是否有 GPU, 描述文本)。"""
    smi = shutil.which("nvidia-smi")
    if not smi:
        return False, "未找到 nvidia-smi"
    try:
        out = subprocess.check_output(
            [smi, "--query-gpu=name,driver_version", "--format=csv,noheader"],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()
        return True, out.splitlines()[0] if out else "NVIDIA GPU"
    except Exception as exc:  # noqa: BLE001
        return False, f"nvidia-smi 调用失败: {exc}"


def detect_cuda_index() -> List[str]:
    """按本机 Python 可用性返回候选 PyTorch 索引（优先新 CUDA）。"""
    # Python 3.14 + Win 实测可用 cu128 / cu126
    return [
        "https://download.pytorch.org/whl/cu128",
        "https://download.pytorch.org/whl/cu126",
        "https://download.pytorch.org/whl/cu124",
        "https://download.pytorch.org/whl/cu121",
    ]


def pip_install(
    packages: Sequence[str],
    extra_args: Optional[Sequence[str]] = None,
    force_reinstall: bool = False,
) -> int:
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if force_reinstall:
        cmd.append("--force-reinstall")
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(packages)
    return run(cmd, check=False)


def install_core() -> None:
    print("=== [1/4] 安装核心依赖 requirements.txt ===")
    if not REQ.exists():
        print(f"[!] 缺少 {REQ}")
        raise SystemExit(1)
    code = pip_install(["-r", str(REQ)])
    if code != 0:
        print("[!] 核心依赖安装失败")
        raise SystemExit(code)
    print("[+] 核心依赖完成")


def install_torch(cpu_only: bool = False) -> None:
    print("=== [2/4] 安装 PyTorch ===")
    has_gpu, gpu_info = detect_nvidia()
    print(f"[*] GPU 探测: has_gpu={has_gpu} · {gpu_info}")

    if cpu_only or not has_gpu:
        print("[*] 安装 CPU 版 torch ...")
        code = pip_install(["torch", "torchvision", "torchaudio"])
        if code != 0:
            print("[!] CPU torch 安装失败")
            raise SystemExit(code)
        return

    # 先卸掉可能存在的 CPU 轮子，避免 pip 认为 “已满足” 而跳过 CUDA 构建
    print("[*] 卸载现有 torch/torchvision/torchaudio（若有）...")
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"],
        check=False,
    )

    last_err = None
    for index in detect_cuda_index():
        print(f"[*] 尝试 CUDA 索引: {index}")
        code = pip_install(
            ["torch", "torchvision", "torchaudio"],
            extra_args=["--index-url", index],
            force_reinstall=True,
        )
        if code == 0:
            verify = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import torch; print(torch.__version__); print(torch.cuda.is_available()); "
                    "print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')",
                ],
                capture_output=True,
                text=True,
            )
            print(verify.stdout.strip() or verify.stderr.strip())
            if verify.returncode == 0 and "True" in (verify.stdout or ""):
                print(f"[+] CUDA torch 安装成功 ({index})")
                return
            if verify.returncode == 0:
                print("[!] torch 已装但 cuda.is_available()=False，继续尝试其他索引...")
                last_err = "cuda not available"
                continue
            last_err = verify.stderr
            continue
        last_err = f"pip exit {code}"

    print("[!] 所有 CUDA 索引失败，回退 CPU 版 torch")
    if last_err:
        print(f"    原因摘要: {last_err}")
    code = pip_install(["torch", "torchvision", "torchaudio"])
    if code != 0:
        raise SystemExit(code)


def install_yolo_extras() -> None:
    print("=== [3/4] 安装 YOLO / 视觉增强 ===")
    # ultralytics 已在 requirements.txt；这里再确保并尝试 onnxruntime-gpu
    pip_install(["ultralytics>=8.3.0"])
    has_gpu, _ = detect_nvidia()
    if has_gpu:
        print("[*] 尝试 onnxruntime-gpu（失败可忽略）...")
        pip_install(["onnxruntime-gpu"])
    else:
        pip_install(["onnxruntime"])


def install_frontend() -> None:
    print("=== [4/4] 安装前端 (web-ui) ===")
    if not (WEB_UI / "package.json").exists():
        print("[!] 未找到 web-ui/package.json，跳过前端")
        return
    npm = shutil.which("npm")
    if not npm:
        print("[!] 未找到 npm，请先安装 Node.js 18+")
        return
    run([npm, "install"], check=False)
    # 生产构建（可选失败）
    run([npm, "run", "build"], check=False)


def print_summary() -> None:
    print("\n=== 环境摘要 ===")
    print(f"Python: {sys.version.split()[0]}  {sys.executable}")
    has_gpu, gpu_info = detect_nvidia()
    print(f"GPU:    {gpu_info if has_gpu else '无'}")
    for mod in ("torch", "ultralytics", "cv2", "selenium", "PIL"):
        try:
            m = __import__(mod if mod != "PIL" else "PIL")
            ver = getattr(m, "__version__", "?")
            extra = ""
            if mod == "torch":
                import torch

                extra = f" cuda={torch.cuda.is_available()}"
                if torch.cuda.is_available():
                    extra += f" device={torch.cuda.get_device_name(0)}"
            print(f"  {mod}: {ver}{extra}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {mod}: 未安装 ({exc.__class__.__name__})")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="DamaiHelper 一键依赖安装")
    parser.add_argument("--skip-torch", action="store_true", help="跳过 PyTorch")
    parser.add_argument("--cpu-only", action="store_true", help="强制 CPU 版 torch")
    parser.add_argument("--with-frontend", action="store_true", help="同时 npm install + build")
    parser.add_argument("--only-frontend", action="store_true", help="只装前端")
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    print("===================================================")
    print("  DamaiHelper 依赖安装器")
    print(f"  项目根目录: {ROOT}")
    print("===================================================")

    if args.only_frontend:
        install_frontend()
        return 0

    install_core()
    if not args.skip_torch:
        install_torch(cpu_only=args.cpu_only)
    install_yolo_extras()
    if args.with_frontend:
        install_frontend()
    print_summary()
    print("\n[+] 全部完成。启动: python web_server.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
