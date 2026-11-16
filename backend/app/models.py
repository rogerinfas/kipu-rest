from typing import Literal

from pydantic import BaseModel, field_validator

Point = tuple[float, float]


class Detection(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float


class Zone(BaseModel):
    """Mesa: polígono con coordenadas normalizadas 0..1."""

    id: str
    name: str
    polygon: list[Point]

    @field_validator("polygon")
    @classmethod
    def _min_points(cls, v: list[Point]) -> list[Point]:
        if len(v) < 3:
            raise ValueError("polygon needs at least 3 points")
        return v


Status = Literal["LIBRE", "ATENCION", "OPTIMO", "ALERTA"]


class TableState(BaseModel):
    id: str
    name: str
    status: Status
    people: int
    elapsed_s: float
    stage: str | None
    amount: float
    stage_note: str


class SalonState(BaseModel):
    tables: list[TableState]
    occupancy_pct: int
    avg_occupancy_s: float
    rotations: int
    hint: str
    fps: float = 0.0
    device: str = "cpu"
