KEY_TERMS = [
    "limitation", "however", "gap", "challenge",
    "future", "trade-off", "contrast", "weakness"
]


def insight_depth_score(answer: str) -> float:
    if not answer:
        return 0.0

    count = sum(1 for k in KEY_TERMS if k in answer.lower())
    return min(1.0, count / 4)
