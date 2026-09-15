def weekly_to_daily(weekly: list[bool], daily: list[bool]) -> list[bool]:
    if len(weekly) != len(daily):
        raise ValueError("weekly and daily results must have the same length")
    return [w and d for w, d in zip(weekly, daily)]
