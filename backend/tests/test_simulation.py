from app.simulation import TableScript, table_seed


def test_script_deterministic():
    a, b = TableScript(42), TableScript(42)
    for t in (0, 90, 300, 700, 1200):
        assert a.stage(t) == b.stage(t)
        assert a.amount(t) == b.amount(t)


def test_script_stage_order_and_ranges():
    for seed in range(50):
        s = TableScript(seed)
        sent_end, wait_end = s.stage_ends
        assert 60 <= sent_end <= 180
        assert 240 <= wait_end - sent_end <= 840
        assert s.stage(0) == "sentados"
        assert s.stage(sent_end + 1) == "esperando"
        assert s.stage(wait_end + 1) == "consumiendo"
        assert s.amount(wait_end - 1) == 0
        assert 40 <= s.amount(wait_end + 3600) <= 180


def test_table_seed_stable():
    assert table_seed("m01", 1) == table_seed("m01", 1)
    assert table_seed("m01", 1) != table_seed("m01", 2)
