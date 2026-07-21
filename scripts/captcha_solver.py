# coding: utf-8
"""验证码求解（OCR 可用时真识别，否则返回占位结果）。"""

from __future__ import annotations

import os
from typing import Optional


def solve_captcha(image_path: str) -> str:
    """识别图片验证码文本。

    - 文件不存在时返回空串
    - 未安装 pillow/pytesseract 时返回 mock 结果，保证编排链路可跑通
    """
    if not image_path or not os.path.exists(image_path):
        return ""

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "MOCK_CAPTCHA"

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return (text or "").strip()
    except Exception:
        return ""


def solve_slider_offset(track_hint: Optional[int] = None) -> int:
    """滑块偏移量求解占位：返回逻辑偏移像素。"""
    if track_hint is not None:
        return int(track_hint)
    return 170
