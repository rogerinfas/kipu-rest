import pytest

from app.config import Settings
from app.models import Detection, Zone
from app.simulation import TableScript, table_seed
from app.tracker import SalonTracker

W = H = 1000
SQ1 = [(0.0, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)]
SQ2 = [(0.5, 0.5), (1.0, 0.5), (1.0, 1.0), (0.5, 1.0)]


def person_in_zone1() -> Detection:
    # foot point (0.25, 0.4) -> inside SQ1
    return Detection(x1=200, y1=100, x2=300, y2=400, conf=0.9)


def make(z1_id: str = "m01") -> SalonTracker:
    zones = [Zone(id=z1_id, name="Mesa 01", polygon=SQ1), Zone(id="m02", name="Mesa 02", polygon=SQ2)]
    return SalonTracker(zones, Settings())


def run(tr: SalonTracker, dets, t0: float, t1: float, step: float = 0.1) -> float:
    t = t0
    while t <= t1 + 1e-9:
        tr.update(dets, W, H, t)
        t += step
    return t1


def table(tr, now, idx=0):
    return tr.snapshot(now).tables[idx]


def test_occupies_after_2s():
    tr = make()
    run(tr, [person_in_zone1()], 0, 1.9)
    assert table(tr, 1.9).status == "LIBRE"
    run(tr, [person_in_zone1()], 2.0, 2.1)
    assert table(tr, 2.1).status == "ATENCION"


def test_brief_dropout_does_not_free_table():
    tr = make()
    run(tr, [person_in_zone1()], 0, 10)
    before = table(tr, 10).elapsed_s
    run(tr, [], 10.1, 11.0)
    run(tr, [person_in_zone1()], 11.1, 12)
    t = table(tr, 12)
    assert t.status != "LIBRE"
    assert t.elapsed_s > before


def test_frees_after_5s_counts_rotation():
    tr = make()
    run(tr, [person_in_zone1()], 0, 2.0)  # confirmed ~2.0
    run(tr, [person_in_zone1()], 2.1, 32.0)
    run(tr, [], 32.1, 37.2)
    s = tr.snapshot(37.2)
    assert s.tables[0].status == "LIBRE"
    assert s.rotations == 1
    assert s.avg_occupancy_s == pytest.approx(30 * 20, abs=20 * 0.3)


def test_elapsed_uses_time_factor():
    tr = make()
    run(tr, [person_in_zone1()], 0, 2.0)
    run(tr, [person_in_zone1()], 2.1, 32.0)
    assert table(tr, 32.0).elapsed_s == pytest.approx(600, abs=1)


def test_alert_when_waiting_over_threshold():
    # pick a zone id whose first occupation waits past 10.5 shown minutes
    zid = next(
        f"t{i}" for i in range(500) if TableScript(table_seed(f"t{i}", 1)).stage_ends[1] > 10.5 * 60
    )
    tr = make(zid)
    run(tr, [person_in_zone1()], 0, 2.0)
    real = 10.5 * 60 / 20
    run(tr, [person_in_zone1()], 2.1, 2.0 + real, step=0.5)
    s = tr.snapshot(2.0 + real)
    assert s.tables[0].status == "ALERTA"
    assert s.tables[0].stage == "esperando"
    assert "Mesa 01" in s.hint


def test_loop_reset_clears_tables_keeps_kpis():
    tr = make()
    run(tr, [person_in_zone1()], 0, 10)
    run(tr, [], 10.1, 15.5)
    run(tr, [person_in_zone1()], 15.6, 20)
    tr.reset_tables()
    s = tr.snapshot(20)
    assert all(t.status == "LIBRE" and t.elapsed_s == 0 for t in s.tables)
    assert s.rotations == 1


def test_occupancy_pct():
    tr = make()
    run(tr, [person_in_zone1()], 0, 3)
    assert tr.snapshot(3).occupancy_pct == 50


def test_no_zones_is_safe():
    tr = SalonTracker([], Settings())
    tr.update([person_in_zone1()], W, H, 1.0)
    s = tr.snapshot(1.0)
    assert s.tables == [] and s.occupancy_pct == 0


def test_cycle_reset_counts_occupied_as_rotations():
    tr = make()
    run(tr, [person_in_zone1()], 0, 2.0)
    run(tr, [person_in_zone1()], 2.1, 12.0)
    tr.reset_tables(now=12.0, close_occupied=True)
    s = tr.snapshot(12.0)
    assert s.rotations == 1
    assert s.avg_occupancy_s == pytest.approx(10 * 20, abs=20 * 0.3)
    assert s.tables[0].status == "LIBRE"
