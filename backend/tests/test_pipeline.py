import time

import cv2
import numpy as np

from app.config import Settings
from app.pipeline import VideoPipeline


class FakeDetector:
    device = "fake"

    def detect(self, frame):
        return []


def _tiny_video(path, frames=6, fps=24):
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (64, 48))
    for i in range(frames):
        w.write(np.full((48, 64, 3), i * 40, np.uint8))
    w.release()


def test_reader_keeps_looping_short_video(tmp_path):
    video = tmp_path / "v.avi"
    _tiny_video(video)
    s = Settings()
    s.video_path = video
    s.zones_path = tmp_path / "z.json"
    p = VideoPipeline(s, lambda st: FakeDetector())
    p.start()
    try:
        seen = set()
        t0 = time.monotonic()
        while time.monotonic() - t0 < 1.0:  # ~4 vueltas de un clip de 0,25 s
            f = p._frame
            if f is not None:
                seen.add(int(f[0, 0, 0]))
            time.sleep(0.01)
        jpg_a = p.latest_jpeg()
        time.sleep(0.1)
        assert p.video_ok
        assert len(seen) >= 4
        assert p.latest_jpeg() is not None and p.latest_jpeg() is not jpg_a
    finally:
        p.stop()
