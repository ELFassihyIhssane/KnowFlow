import re
from collections import Counter
from typing import List

HEADER_FOOTER_MIN_REPEAT = 3  
HEADER_MIN_LEN = 25           


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _remove_pdf_artifacts(text: str) -> str:

    text = text.replace("\x00", " ")

    text = re.sub(r"\(cid:[0-9]+\)", " ", text)

    text = text.replace("ˆ", "")

    text = re.sub(r"[ \t]+", " ", text)

    return text


def _remove_obvious_noise_lines(lines: List[str]) -> List[str]:
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            cleaned.append("")
            continue

        if len(s) <= 3 and re.fullmatch(r"[0-9\W]+", s):
            continue

        if len(s) <= 2 and s.isalpha():
            continue

        letters = sum(ch.isalpha() for ch in s)

        if re.fullmatch(r"([A-Za-z]\s+){1,}[A-Za-z]", s):
            continue

        if s.count(" ") > letters and letters < 10:
            continue

        if letters / max(len(s), 1) < 0.25 and len(s) < 40:
            continue

        chunks = re.split(r"\s{2,}", s)
        if len(chunks) >= 3 and not re.search(r"[\.!?;:]", s):
            continue

        math_symbols = "=+-−*/<>≤≥∑∏∫()[]{}_^%|,:;"
        math_like = sum(ch.isdigit() or ch in math_symbols for ch in s)

        if len(s) < 15 and math_like > 0 and not re.search(r"[\.!?]", s):
            continue

        if math_like > 0 and math_like / len(s) > 0.4 and not re.search(r"[\.!?]", s):
            continue

        cleaned.append(s)

    return cleaned


def _remove_repeated_headers(lines: List[str]) -> List[str]:
    freq = Counter(lines)
    seen = set()
    out = []

    for line in lines:
        s = line.strip()
        if not s:
            out.append("")
            continue

        if (
            freq[s] >= HEADER_FOOTER_MIN_REPEAT
            and len(s) >= HEADER_MIN_LEN
            and s.upper() == s  
        ):
            if s in seen:
                continue
            seen.add(s)

        out.append(s)

    return out


def _merge_lines_into_paragraphs(lines: List[str]) -> str:

    paragraphs: List[str] = []
    buffer: List[str] = []

    def flush_buffer():
        if not buffer:
            return
        paragraphs.append(" ".join(buffer))
        buffer.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush_buffer()
            continue

        if buffer:
            prev = buffer[-1]
            if prev.endswith("-") and not prev.endswith("--"):
                buffer[-1] = prev[:-1] + s
            else:
                buffer.append(s)
        else:
            buffer.append(s)

    flush_buffer()
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()]

    return "\n\n".join(paragraphs)


def clean_raw_text(raw_text: str) -> str:

    if not raw_text:
        return ""

    text = _normalize_newlines(raw_text)

    text = _remove_pdf_artifacts(text)

    lines = text.split("\n")

    lines = _remove_obvious_noise_lines(lines)

    lines = _remove_repeated_headers(lines)

    cleaned = _merge_lines_into_paragraphs(lines)

    return cleaned.strip()
