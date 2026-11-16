import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


class FakeDetector:
    device = "fake"

    def detect(self, frame):
        return []


@pytest.fixture
def client(tmp_path):
    s = Settings()
    s.video_path = tmp_path / "missing.mp4"
    s.zones_path = tmp_path / "zones.json"
    app = create_app(s, detector_factory=lambda st: FakeDetector())
    with TestClient(app) as c:
        yield c


def test_health_without_video(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["video_ok"] is False
    assert body["zones"] == 0


def test_zones_put_get(client):
    zs = [{"id": "m01", "name": "Mesa 01", "polygon": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3]]}]
    assert client.put("/api/zones", json=zs).status_code == 200
    got = client.get("/api/zones").json()
    assert got[0]["id"] == "m01"
    assert client.get("/api/health").json()["zones"] == 1


def test_zones_put_rejects_bad_polygon(client):
    zs = [{"id": "m01", "name": "Mesa 01", "polygon": [[0.1, 0.1], [0.3, 0.1]]}]
    assert client.put("/api/zones", json=zs).status_code == 422


def test_ws_sends_state(client):
    with client.websocket_connect("/ws/state") as ws:
        data = ws.receive_json()
    assert "tables" in data and "hint" in data


def test_ws_disconnect_is_harmless(client):
    with client.websocket_connect("/ws/state") as ws:
        ws.receive_json()
    with client.websocket_connect("/ws/state") as ws:
        assert "tables" in ws.receive_json()
    assert client.get("/api/health").status_code == 200


def test_frame_without_video_is_503(client):
    assert client.get("/api/frame.jpg").status_code == 503
