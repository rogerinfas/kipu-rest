import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    return os.environ.get(f"KIPU_{name}", default)


@dataclass
class Settings:
    video_path: Path = field(
        default_factory=lambda: Path(_env("VIDEO", str(BACKEND_DIR / "media" / "flow-salon-v1.mp4")))
    )
    zones_path: Path = field(
        default_factory=lambda: Path(_env("ZONES", str(BACKEND_DIR / "zones" / "salon.json")))
    )
    model_name: str = field(default_factory=lambda: _env("MODEL", "yolo11n.pt"))
    alert_min: float = field(default_factory=lambda: float(_env("ALERT_MIN", "10")))
    time_factor: float = field(default_factory=lambda: float(_env("TIME_FACTOR", "20")))
    occupy_s: float = field(default_factory=lambda: float(_env("OCCUPY_S", "2.0")))
    release_s: float = field(default_factory=lambda: float(_env("RELEASE_S", "5.0")))
    attention_min: float = field(default_factory=lambda: float(_env("ATTENTION_MIN", "3")))
    conf: float = field(default_factory=lambda: float(_env("CONF", "0.35")))
    imgsz: int = field(default_factory=lambda: int(_env("IMGSZ", "960")))
    port: int = field(default_factory=lambda: int(_env("PORT", "5000")))
