from typing import List
import re


GAP_PATTERNS = [
    r"not evaluated",
    r"limited to",
    r"future work",
    r"not explored",
    r"lack of",
    r"remains unclear",
]


def detect_gaps(texts: List[str]) -> List[str]:
    gaps = set()
    joined = " ".join(texts).lower()

    for pat in GAP_PATTERNS:
        if re.search(pat, joined):
            gaps.add(f"Potential gap detected: '{pat}'")

    return list(gaps)
