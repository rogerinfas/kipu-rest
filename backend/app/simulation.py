"""Datos de negocio simulados (etapa del servicio y monto). No se detectan."""

import random
import zlib
from typing import Literal

Stage = Literal["sentados", "esperando", "consumiendo"]

AMOUNT_RAMP_S = 300.0  # el monto crece durante 5 min mostrados de consumo


def table_seed(zone_id: str, occupation_n: int) -> int:
    """Semilla estable entre ejecuciones (hash() de Python no lo es)."""
    return zlib.crc32(f"{zone_id}:{occupation_n}".encode())


class TableScript:
    """Guion fijo de una ocupación: sentados -> esperando -> consumiendo."""

    def __init__(self, seed: int):
        rng = random.Random(seed)
        sent = rng.uniform(60, 180)
        wait = rng.uniform(240, 840)
        self.stage_ends: tuple[float, float] = (sent, sent + wait)
        self.final_amount: float = round(rng.uniform(40, 180))

    def stage(self, elapsed_shown_s: float) -> Stage:
        sent_end, wait_end = self.stage_ends
        if elapsed_shown_s < sent_end:
            return "sentados"
        if elapsed_shown_s < wait_end:
            return "esperando"
        return "consumiendo"

    def amount(self, elapsed_shown_s: float) -> float:
        start = self.stage_ends[1]
        if elapsed_shown_s < start:
            return 0.0
        frac = min(1.0, (elapsed_shown_s - start) / AMOUNT_RAMP_S)
        return round(self.final_amount * max(frac, 0.25))
