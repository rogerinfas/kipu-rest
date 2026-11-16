from app.models import Detection, Point


def foot_point(d: Detection, w: int, h: int) -> Point:
    """Punto inferior-centro de la caja, normalizado 0..1."""
    return ((d.x1 + d.x2) / 2 / w, d.y2 / h)


def point_in_polygon(p: Point, poly: list[Point]) -> bool:
    """Ray casting."""
    x, y = p
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
