import pytest
from pydantic import ValidationError

from app.models import Zone
from app.zones import load_zones, save_zones

SQ = [(0.1, 0.1), (0.3, 0.1), (0.3, 0.3)]


def test_roundtrip(tmp_path):
    p = tmp_path / "z.json"
    zs = [Zone(id="m01", name="Mesa 01", polygon=SQ)]
    save_zones(p, zs)
    assert load_zones(p) == zs


def test_missing_zones_file_returns_empty(tmp_path):
    assert load_zones(tmp_path / "nope.json") == []


def test_invalid_json_returns_empty(tmp_path):
    p = tmp_path / "z.json"
    p.write_text("{not json")
    assert load_zones(p) == []


def test_rejects_polygon_under_3_points(tmp_path):
    with pytest.raises((ValueError, ValidationError)):
        save_zones(tmp_path / "z.json", [Zone(id="x", name="x", polygon=[(0, 0), (1, 1)])])
