# coding: utf-8
"""YOLO 推理封装：验证码/UI 目标检测逻辑层。

- 优先使用本机 CUDA + ultralytics
- 无模型 / 无依赖时自动 mock，保证编排链路可跑通
- 不要求真实抢票成功率
"""

from __future__ import annotations

import base64
import io
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .device_probe import environment_report

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
DEFAULT_WEIGHTS = MODELS_DIR / "yolov8n.pt"

# 业务类名（演示用；真实微调模型可替换 names）
CAPTCHA_CLASSES = ("slider", "button", "checkbox", "text", "qrcode", "ticket_card")


@dataclass
class Detection:
    label: str
    confidence: float
    xyxy: Tuple[float, float, float, float]  # x1,y1,x2,y2
    center: Tuple[float, float] = field(init=False)

    def __post_init__(self) -> None:
        x1, y1, x2, y2 = self.xyxy
        self.center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "confidence": round(float(self.confidence), 4),
            "xyxy": [round(float(v), 2) for v in self.xyxy],
            "center": [round(float(v), 2) for v in self.center],
        }


class YoloEngine:
    """懒加载 YOLO 引擎（线程安全）。"""

    def __init__(
        self,
        weights: Optional[os.PathLike] = None,
        device: Optional[str] = None,
        conf: float = 0.35,
    ) -> None:
        self.weights = Path(weights) if weights else DEFAULT_WEIGHTS
        self.device_pref = device  # None=auto
        self.conf = conf
        self._lock = threading.RLock()
        self._model = None
        self._device: str = "cpu"
        self._mock_mode = False
        self._load_error: Optional[str] = None
        self._last_infer_ms: float = 0.0

    # ------------------------------------------------------------------
    @property
    def ready(self) -> bool:
        return self._model is not None or self._mock_mode

    @property
    def mock_mode(self) -> bool:
        return self._mock_mode

    def status(self) -> Dict[str, Any]:
        env = environment_report()
        return {
            "engine_loaded": self._model is not None,
            "mock_mode": self._mock_mode,
            "device": self._device,
            "weights": str(self.weights),
            "weights_exists": self.weights.exists(),
            "conf": self.conf,
            "last_infer_ms": self._last_infer_ms,
            "load_error": self._load_error,
            "environment": env,
        }

    def ensure_loaded(self, allow_download: bool = False) -> Dict[str, Any]:
        with self._lock:
            if self._model is not None or self._mock_mode:
                return self.status()
            return self._load(allow_download=allow_download)

    def _resolve_device(self) -> str:
        if self.device_pref:
            return self.device_pref
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda:0"
        except ImportError:
            pass
        return "cpu"

    def _load(self, allow_download: bool = False) -> Dict[str, Any]:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            self._mock_mode = True
            self._load_error = f"ultralytics 未安装: {exc}"
            self._device = "mock"
            return self.status()

        self._device = self._resolve_device()
        weights_path = self.weights

        # 允许使用官方小模型名（yolov8n.pt），ultralytics 会自动下载
        source: Union[str, Path]
        if weights_path.exists():
            source = weights_path
        elif allow_download:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            source = weights_path.name if weights_path.suffix == ".pt" else "yolov8n.pt"
        else:
            # 不强制下载：进入 mock，避免一键脚本外偷偷拉大文件
            self._mock_mode = True
            self._load_error = f"权重不存在: {weights_path}（可 POST /api/ai/load 触发下载）"
            self._device = self._device
            return self.status()

        try:
            model = YOLO(str(source))
            # 轻量预热：不强制跑图
            self._model = model
            self._mock_mode = False
            self._load_error = None
            # 若下载到了默认缓存，尽量拷到 models/
            if not weights_path.exists() and allow_download:
                try:
                    # ultralytics 通常把权重放在 cwd 或用户目录；若当前目录有同名则移动
                    cwd_pt = Path.cwd() / Path(str(source)).name
                    if cwd_pt.exists() and cwd_pt.resolve() != weights_path.resolve():
                        MODELS_DIR.mkdir(parents=True, exist_ok=True)
                        cwd_pt.replace(weights_path)
                except Exception:
                    pass
        except Exception as exc:  # noqa: BLE001
            self._mock_mode = True
            self._model = None
            self._load_error = f"模型加载失败: {exc}"
        return self.status()

    # ------------------------------------------------------------------
    def detect(
        self,
        image: Any,
        conf: Optional[float] = None,
        classes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """对图片做检测。image 可为路径 / ndarray / PIL / bytes / base64。"""
        self.ensure_loaded(allow_download=False)
        t0 = time.perf_counter()

        if self._mock_mode or self._model is None:
            dets = self._mock_detect(image)
            self._last_infer_ms = (time.perf_counter() - t0) * 1000
            return self._pack(dets, mock=True)

        try:
            import numpy as np

            arr = self._to_ndarray(image)
            results = self._model.predict(
                source=arr,
                conf=conf if conf is not None else self.conf,
                device=self._device,
                verbose=False,
            )
            dets: List[Detection] = []
            if results:
                r0 = results[0]
                names = r0.names if hasattr(r0, "names") else {}
                boxes = getattr(r0, "boxes", None)
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls.item()) if hasattr(box.cls, "item") else int(box.cls)
                        label = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id)
                        if classes and label not in classes:
                            continue
                        conf_v = float(box.conf.item()) if hasattr(box.conf, "item") else float(box.conf)
                        xyxy = box.xyxy[0].tolist() if hasattr(box.xyxy, "tolist") else list(box.xyxy[0])
                        dets.append(
                            Detection(
                                label=str(label),
                                confidence=conf_v,
                                xyxy=(float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])),
                            )
                        )
            self._last_infer_ms = (time.perf_counter() - t0) * 1000
            return self._pack(dets, mock=False)
        except Exception as exc:  # noqa: BLE001
            # 推理失败则 mock，保证链路
            dets = self._mock_detect(image)
            self._last_infer_ms = (time.perf_counter() - t0) * 1000
            payload = self._pack(dets, mock=True)
            payload["error"] = str(exc)
            return payload

    def solve_slider(self, image: Any = None) -> Dict[str, Any]:
        """滑块验证码逻辑：检测滑块/缺口，返回建议拖拽偏移。"""
        result = self.detect(image) if image is not None else {
            "detections": [
                Detection("slider", 0.91, (20, 200, 60, 240)).to_dict(),
                Detection("button", 0.88, (170, 200, 210, 240)).to_dict(),
            ],
            "mock": True,
            "count": 2,
        }
        dets = result.get("detections") or []
        slider = next((d for d in dets if d.get("label") in ("slider", "button")), None)
        # 演示：若有两个目标，用中心差；否则默认 170
        offset = 170
        if len(dets) >= 2:
            c0 = dets[0].get("center") or [0, 0]
            c1 = dets[1].get("center") or [0, 0]
            offset = int(abs(c1[0] - c0[0])) or 170
        elif slider:
            offset = int((slider.get("center") or [170, 0])[0])

        return {
            "offset_px": offset,
            "confidence": float(slider["confidence"]) if slider else 0.8,
            "device": self._device,
            "mock": result.get("mock", self._mock_mode),
            "detections": dets,
            "infer_ms": self._last_infer_ms,
            "message": f"建议拖拽偏移 {offset}px",
        }

    # ------------------------------------------------------------------
    def _pack(self, dets: List[Detection], mock: bool) -> Dict[str, Any]:
        return {
            "detections": [d.to_dict() for d in dets],
            "count": len(dets),
            "mock": mock,
            "device": self._device if not mock else "mock",
            "infer_ms": round(self._last_infer_ms, 2),
            "weights": str(self.weights),
        }

    def _mock_detect(self, image: Any) -> List[Detection]:
        w, h = self._image_size(image)
        # 相对布局的伪检测框
        return [
            Detection("slider", 0.93, (w * 0.05, h * 0.72, w * 0.18, h * 0.88)),
            Detection("button", 0.89, (w * 0.55, h * 0.72, w * 0.68, h * 0.88)),
            Detection("ticket_card", 0.86, (w * 0.1, h * 0.2, w * 0.9, h * 0.55)),
        ]

    def _image_size(self, image: Any) -> Tuple[float, float]:
        try:
            arr = self._to_ndarray(image)
            h, w = arr.shape[:2]
            return float(w), float(h)
        except Exception:
            return 320.0, 160.0

    def _to_ndarray(self, image: Any):
        import numpy as np

        if image is None:
            return np.zeros((160, 320, 3), dtype=np.uint8)

        if isinstance(image, np.ndarray):
            return image

        if isinstance(image, (bytes, bytearray)):
            return self._bytes_to_array(bytes(image))

        if isinstance(image, str):
            # data URL or path or pure base64
            if image.startswith("data:"):
                b64 = image.split(",", 1)[-1]
                return self._bytes_to_array(base64.b64decode(b64))
            if os.path.exists(image):
                try:
                    import cv2

                    arr = cv2.imread(image)
                    if arr is not None:
                        return arr
                except ImportError:
                    from PIL import Image
                    import numpy as np

                    return np.array(Image.open(image).convert("RGB"))
            # try base64
            try:
                return self._bytes_to_array(base64.b64decode(image))
            except Exception as exc:
                raise ValueError("无法解析 image 字符串") from exc

        # PIL
        if hasattr(image, "convert"):
            import numpy as np

            return np.array(image.convert("RGB"))

        raise TypeError(f"不支持的 image 类型: {type(image)}")

    def _bytes_to_array(self, data: bytes):
        try:
            import cv2
            import numpy as np

            arr = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("imdecode failed")
            return img
        except Exception:
            from PIL import Image
            import numpy as np

            return np.array(Image.open(io.BytesIO(data)).convert("RGB"))


# 全局单例
engine = YoloEngine()
