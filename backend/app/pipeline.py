"""Lectura del video a velocidad real + inferencia en otro hilo sobre el último frame."""

import logging
import threading
import time
from typing import Callable, Protocol

import cv2
import numpy as np

from app.config import Settings
from app.models import Detection, SalonState, Zone
from app.tracker import SalonTracker
from app.zones import load_zones

log = logging.getLogger(__name__)

STREAM_W = 1280  # ancho del MJPEG (ahorra CPU y ancho de banda)
# BGR
COLORS = {
    "LIBRE": (112, 123, 138),
    "ATENCION": (58, 164, 224),
    "OPTIMO": (78, 143, 107),
    "ALERTA": (43, 69, 210),
}
PERSON_COLOR = (221, 235, 245)


class DetectorLike(Protocol):
    device: str

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]: ...


def _clock(seconds: float) -> str:
    s = int(seconds)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _short(name: str) -> str:
    parts = name.split()
    return f"M{parts[-1]}" if len(parts) > 1 and parts[-1].isdigit() else name


class VideoPipeline:
    def __init__(self, settings: Settings, detector_factory: Callable[[Settings], DetectorLike]):
        self.settings = settings
        self._factory = detector_factory
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._new_frame = threading.Event()
        self._frame: np.ndarray | None = None
        self._jpeg: bytes | None = None
        self._dets: list[Detection] = []
        self._fps = 0.0
        self.device = "cargando"
        self.video_ok = False
        self.zones: list[Zone] = load_zones(settings.zones_path)
        self._tracker = SalonTracker(self.zones, settings)
        self._threads: list[threading.Thread] = []

    # ---- ciclo de vida
    def start(self) -> None:
        self.video_ok = self._probe()
        for fn in (self._reader, self._inferer):
            t = threading.Thread(target=fn, daemon=True, name=fn.__name__)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        if self._stop.is_set():
            return
        self._stop.set()
        self._new_frame.set()
        for t in self._threads:
            t.join(timeout=3)

    def _probe(self) -> bool:
        if not self.settings.video_path.exists():
            log.error("No existe el video %s", self.settings.video_path)
            return False
        cap = cv2.VideoCapture(str(self.settings.video_path))
        ok = cap.isOpened() and cap.read()[0]
        cap.release()
        return bool(ok)

    # ---- API pública
    @property
    def stopped(self) -> bool:
        return self._stop.is_set()

    def set_zones(self, zones: list[Zone]) -> None:
        with self._lock:
            self.zones = zones
            self._tracker = SalonTracker(zones, self.settings)

    def state(self) -> SalonState:
        with self._lock:
            s = self._tracker.snapshot(time.monotonic())
        s.fps = round(self._fps, 1)
        s.device = self.device
        return s

    def latest_jpeg(self) -> bytes | None:
        return self._jpeg

    def clean_jpeg(self) -> bytes | None:
        f = self._frame
        if f is None:
            return None
        ok, buf = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return buf.tobytes() if ok else None

    # ---- hilos
    def _reader(self) -> None:
        if not self.video_ok:
            return
        cap = cv2.VideoCapture(str(self.settings.video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        period = 1.0 / fps
        nxt = time.monotonic()
        last_reset = nxt
        fails = 0
        while not self._stop.is_set():
            ok, frame = cap.read()
            if not ok:
                fails += 1
                if fails > 1:
                    # el rebobinado no funcionó (pasa con algunos backends en Windows): reabrir
                    if fails % 50 == 0:
                        log.warning("No se puede leer el video tras %d intentos", fails)
                    cap.release()
                    time.sleep(period)
                    cap = cv2.VideoCapture(str(self.settings.video_path))
                    continue
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                if time.monotonic() - last_reset >= self.settings.cycle_s:
                    last_reset = time.monotonic()
                    with self._lock:
                        self._tracker.reset_tables(now=last_reset, close_occupied=True)
                continue
            fails = 0
            self._frame = frame
            self._new_frame.set()
            self._jpeg = self._annotate(frame)
            nxt += period
            delay = nxt - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                nxt = time.monotonic()  # vamos atrasados: no acumular deuda
        cap.release()

    def _inferer(self) -> None:
        try:
            detector = self._factory(self.settings)
            self.device = detector.device
        except Exception:
            log.exception("No se pudo cargar el detector")
            self.device = "error"
            return
        last = time.monotonic()
        while not self._stop.is_set():
            if not self._new_frame.wait(timeout=0.5):
                continue
            self._new_frame.clear()
            frame = self._frame
            if frame is None:
                continue
            try:
                dets = detector.detect(frame)
            except Exception:
                if self._stop.is_set():
                    break
                log.exception("Fallo de inferencia")
                continue
            h, w = frame.shape[:2]
            now = time.monotonic()
            with self._lock:
                self._tracker.update(dets, w, h, now)
            self._dets = dets
            dt = now - last
            last = now
            if dt > 0:
                self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt) if self._fps else 1.0 / dt

    # ---- dibujo
    def _annotate(self, frame: np.ndarray) -> bytes | None:
        h0, w0 = frame.shape[:2]
        scale = STREAM_W / w0 if w0 > STREAM_W else 1.0
        img = cv2.resize(frame, (int(w0 * scale), int(h0 * scale))) if scale != 1.0 else frame.copy()
        h, w = img.shape[:2]
        state = self.state()
        by_id = {t.id: t for t in state.tables}
        overlay = img.copy()
        polys = []
        for z in self.zones:
            t = by_id.get(z.id)
            status = t.status if t else "LIBRE"
            pts = np.array([[int(x * w), int(y * h)] for x, y in z.polygon], np.int32)
            polys.append((z, t, status, pts))
            if status != "LIBRE":
                cv2.fillPoly(overlay, [pts], COLORS[status])
        img = cv2.addWeighted(overlay, 0.22, img, 0.78, 0)
        for d in self._dets:
            cv2.rectangle(
                img, (int(d.x1 * scale), int(d.y1 * scale)), (int(d.x2 * scale), int(d.y2 * scale)),
                PERSON_COLOR, 1, cv2.LINE_AA,
            )
        for z, t, status, pts in polys:
            color = COLORS[status]
            cv2.polylines(img, [pts], True, color, 2, cv2.LINE_AA)
            label = f"{_short(z.name)} {_clock(t.elapsed_s) if t and status != 'LIBRE' else 'libre'}"
            x, y = pts[:, 0].min(), pts[:, 1].min()
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(img, (x, y - th - 8), (x + tw + 8, y), color, -1)
            cv2.putText(img, label, (x + 4, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (22, 29, 43), 2, cv2.LINE_AA)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return buf.tobytes() if ok else None
