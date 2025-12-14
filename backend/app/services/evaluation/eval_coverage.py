from rapidfuzz import fuzz


def coverage_score(question: str, answer: str) -> float:
    if not question or not answer:
        return 0.0
    return fuzz.token_set_ratio(question, answer) / 100
