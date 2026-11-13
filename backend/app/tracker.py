"""Lógica pura de estados de mesa. Sin I/O: recibe detecciones y un reloj."""

from dataclasses import dataclass, field

from app.config import Settings
from app.geometry import foot_point, point_in_polygon
from app.models import Detection, SalonState, TableState, Zone
from app.simulation import TableScript, table_seed

STAGE_NOTE = {
    "sentados": "Comensales recién sentados",
    "esperando": "Esperando plato fuerte",
}


@dataclass
class _Table:
    zone: Zone
    occupied: bool = False
    people: int = 0
    presence_since: float | None = None
    absence_since: float | None = None
    occupied_at: float = 0.0
    occupations: int = 0
    script: TableScript | None = None

    def free(self) -> None:
        self.occupied = False
        self.presence_since = None
        self.absence_since = None
        self.script = None


@dataclass
class SalonTracker:
    zones: list[Zone]
    settings: Settings
    _tables: list[_Table] = field(init=False)
    _rotations: int = field(init=False, default=0)
    _durations: list[float] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._tables = [_Table(z) for z in self.zones]

    def update(self, dets: list[Detection], w: int, h: int, now: float) -> None:
        feet = [foot_point(d, w, h) for d in dets]
        s = self.settings
        for t in self._tables:
            t.people = sum(1 for p in feet if point_in_polygon(p, t.zone.polygon))
            if not t.occupied:
                if t.people == 0:
                    t.presence_since = None
                    continue
                if t.presence_since is None:
                    t.presence_since = now
                if now - t.presence_since >= s.occupy_s - 1e-9:
                    t.occupied = True
                    t.occupied_at = now
                    t.absence_since = None
                    t.occupations += 1
                    t.script = TableScript(table_seed(t.zone.id, t.occupations))
                continue
            if t.people > 0:
                t.absence_since = None
                continue
            if t.absence_since is None:
                t.absence_since = now
            if now - t.absence_since >= s.release_s - 1e-9:
                self._rotations += 1
                self._durations.append((t.absence_since - t.occupied_at) * s.time_factor)
                t.free()

    def reset_tables(self, now: float | None = None, close_occupied: bool = False) -> None:
        """Libera todas las mesas. Con close_occupied, cuenta las ocupadas como rotaciones."""
        for t in self._tables:
            if close_occupied and t.occupied and now is not None:
                self._rotations += 1
                self._durations.append((now - t.occupied_at) * self.settings.time_factor)
            t.free()
            t.people = 0

    def _table_state(self, t: _Table, now: float) -> TableState:
        s = self.settings
        if not t.occupied or t.script is None:
            return TableState(
                id=t.zone.id, name=t.zone.name, status="LIBRE", people=t.people,
                elapsed_s=0.0, stage=None, amount=0.0, stage_note="Lista para nuevos clientes",
            )
        elapsed = max(0.0, (now - t.occupied_at) * s.time_factor)
        stage = t.script.stage(elapsed)
        amount = t.script.amount(elapsed)
        if stage == "esperando" and elapsed >= s.alert_min * 60:
            status = "ALERTA"
        elif elapsed < s.attention_min * 60:
            status = "ATENCION"
        else:
            status = "OPTIMO"
        note = STAGE_NOTE.get(stage) or f"Consumiendo · S/ {amount:.0f}"
        return TableState(
            id=t.zone.id, name=t.zone.name, status=status, people=t.people,
            elapsed_s=round(elapsed, 1), stage=stage, amount=amount, stage_note=note,
        )

    def snapshot(self, now: float) -> SalonState:
        tables = [self._table_state(t, now) for t in self._tables]
        n = len(tables)
        occupied = sum(1 for t in tables if t.status != "LIBRE")
        pct = round(occupied * 100 / n) if n else 0
        alerts = sorted((t for t in tables if t.status == "ALERTA"), key=lambda t: -t.elapsed_s)
        if alerts:
            hint = f"Priorizar pase de {alerts[0].name} en cocina"
        elif pct > 80:
            hint = "Salón casi lleno: preparar rotación"
        else:
            hint = "Servicio fluido"
        avg = sum(self._durations) / len(self._durations) if self._durations else 0.0
        return SalonState(
            tables=tables, occupancy_pct=pct, avg_occupancy_s=round(avg, 1),
            rotations=self._rotations, hint=hint,
        )
