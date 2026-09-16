from __future__ import annotations


def levels(entry: float, stop: float, multiples: tuple[int, ...] = (1, 2, 3)) -> dict[str, float]:
    if entry <= stop:
        raise ValueError("entry must be above stop")
    risk = entry - stop
    return {f"{n}R": entry + n * risk for n in multiples}


def first_touch(highs: list[float], lows: list[float], levels_: dict[str, float], stop: float) -> str | None:
    for high, low in zip(highs, lows):
        if low <= stop:
            return "STOP"
        for name, target in levels_.items():
            if high >= target:
                return name
    return None
