import pytest

from app.config import BACKEND_DIR

VIDEO = BACKEND_DIR / "media" / "flow-salon-v1.mp4"


@pytest.mark.slow
@pytest.mark.skipif(not VIDEO.exists(), reason="video de demo no disponible")
def test_detects_people_in_salon():
    import cv2

    from app.detector import Detector

    cap = cv2.VideoCapture(str(VIDEO))
    cap.set(cv2.CAP_PROP_POS_MSEC, 3500)
    ok, frame = cap.read()
    cap.release()
    assert ok
    det = Detector("yolo11n.pt", conf=0.35, imgsz=960)
    people = det.detect(frame)
    assert det.device in ("cpu", "cuda:0")
    assert len(people) >= 8
    assert all(p.x2 > p.x1 and p.y2 > p.y1 for p in people)
