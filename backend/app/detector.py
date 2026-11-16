import logging

import numpy as np

from app.models import Detection

log = logging.getLogger(__name__)
PERSON = 0


class Detector:
    """YOLO solo para personas. Usa CUDA si existe, si no CPU."""

    def __init__(self, model_name: str, conf: float, imgsz: int):
        import torch
        from ultralytics import YOLO

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.conf = conf
        self.imgsz = imgsz
        self.model = YOLO(model_name)
        log.info("YOLO %s en %s", model_name, self.device)

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        res = self.model.predict(
            frame_bgr, classes=[PERSON], conf=self.conf, imgsz=self.imgsz,
            device=self.device, verbose=False,
        )[0]
        out: list[Detection] = []
        for (x1, y1, x2, y2), c in zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist()):
            out.append(Detection(x1=x1, y1=y1, x2=x2, y2=y2, conf=c))
        return out
