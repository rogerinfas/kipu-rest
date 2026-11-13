from app.geometry import foot_point, point_in_polygon
from app.models import Detection


def test_foot_point():
    d = Detection(x1=100, y1=100, x2=300, y2=500, conf=0.9)
    assert foot_point(d, 1000, 1000) == (0.2, 0.5)


def test_point_in_square():
    sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert point_in_polygon((0.5, 0.5), sq)
    assert not point_in_polygon((1.5, 0.5), sq)


def test_point_in_concave():
    ell = [(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]
    assert point_in_polygon((0.5, 1.5), ell)
    assert not point_in_polygon((1.5, 1.5), ell)
