import json
import logging
import os
import tempfile
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from app.models import Zone

log = logging.getLogger(__name__)
_zones = TypeAdapter(list[Zone])


def load_zones(path: Path) -> list[Zone]:
    try:
        return _zones.validate_json(Path(path).read_bytes())
    except FileNotFoundError:
        log.warning("Sin archivo de zonas en %s: hay que calibrar", path)
    except (ValidationError, ValueError) as e:
        log.warning("Zonas inválidas en %s: %s", path, e)
    return []


def save_zones(path: Path, zones: list[Zone]) -> None:
    """Escritura atómica: temporal + reemplazo."""
    zones = _zones.validate_python([z.model_dump() for z in zones])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps([z.model_dump() for z in zones], indent=2, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(data)
    os.replace(tmp, path)
