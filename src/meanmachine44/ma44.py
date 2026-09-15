def rising(ma: list[float | None], minimum: int = 3) -> list[bool]:
    if minimum < 2:
        raise ValueError("minimum must be at least 2")

    out = [False] * len(ma)
    for i in range(minimum - 1, len(ma)):
        window = ma[i - minimum + 1:i + 1]
        out[i] = all(v is not None for v in window) and all(
            window[j] > window[j - 1] for j in range(1, minimum)
        )
    return out
