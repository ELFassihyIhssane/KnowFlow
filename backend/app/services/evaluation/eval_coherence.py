def coherence_score(answer: str) -> float:
    if not answer:
        return 0.0

    sentences = [s for s in answer.split(".") if len(s.strip()) > 10]
    if len(sentences) < 2:
        return 0.4

    return min(1.0, len(sentences) / 8)
