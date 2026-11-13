"""Verifica que la laptop está lista para la demo.

Uso (desde backend/):  uv run python ../scripts/check_env.py [--prepare]
--prepare descarga el modelo YOLO si falta (requiere internet).
Sale con código 1 si algo crítico falla.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

OK, FAIL, WARN = "[OK]  ", "[FALLA]", "[AVISO]"
critical_failed = False


def report(status: str, msg: str, critical: bool = True) -> None:
    global critical_failed
    print(f"{status} {msg}")
    if status == FAIL and critical:
        critical_failed = True


def main() -> int:
    prepare = "--prepare" in sys.argv

    v = sys.version_info
    report(OK if v >= (3, 11) else FAIL, f"Python {v.major}.{v.minor}.{v.micro}")

    try:
        import torch

        if torch.cuda.is_available():
            report(OK, f"GPU CUDA: {torch.cuda.get_device_name(0)} (torch {torch.__version__})")
        else:
            report(WARN, f"Sin CUDA: se usará la CPU (torch {torch.__version__})", critical=False)
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"torch no se puede importar: {e}")

    from app.config import Settings

    s = Settings()
    model = Path(s.model_name)
    model_path = model if model.is_absolute() else BACKEND / model
    if model_path.exists():
        report(OK, f"Modelo {model_path.name} presente")
    elif prepare:
        from ultralytics import YOLO

        YOLO(str(model_path))
        report(OK if model_path.exists() else FAIL, f"Modelo {model_path.name} descargado")
    else:
        report(FAIL, f"Falta el modelo {model_path} (ejecuta con --prepare con internet)")

    try:
        import cv2

        cap = cv2.VideoCapture(str(s.video_path))
        ok = cap.isOpened() and cap.read()[0]
        cap.release()
        report(OK if ok else FAIL, f"Video {s.video_path.name}" + ("" if ok else " no se puede leer"))
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"OpenCV: {e}")

    try:
        zones = json.loads(Path(s.zones_path).read_text(encoding="utf-8"))
        report(OK if zones else FAIL, f"{len(zones)} mesas calibradas en {Path(s.zones_path).name}")
    except Exception as e:  # noqa: BLE001
        report(FAIL, f"Zonas: {e}")

    dist = ROOT / "frontend" / "dist" / "index.html"
    report(OK if dist.exists() else FAIL, "Frontend compilado (frontend/dist)" + ("" if dist.exists() else ": ejecuta pnpm build"))

    print("\nTodo listo para la demo." if not critical_failed else "\nHay problemas: revisa las líneas [FALLA].")
    return 1 if critical_failed else 0


if __name__ == "__main__":
    sys.exit(main())
