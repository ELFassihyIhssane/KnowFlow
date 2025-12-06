# app/cleaning/text_cleaning.py

import re
from collections import Counter
from typing import List

HEADER_FOOTER_MIN_REPEAT = 3  # si une ligne revient >= 3 fois, on la considère header/footer
HEADER_MIN_LEN = 25           # long header probable


def _normalize_newlines(text: str) -> str:
    """Unifie les sauts de ligne."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _remove_pdf_artifacts(text: str) -> str:
    """
    Nettoie les artefacts typiques de PDFMiner :
    - (cid:80), (cid:123)...
    - caractères bizarres de surimpression (ˆ, etc.)
    """
    # Null bytes éventuels
    text = text.replace("\x00", " ")

    # (cid:80), (cid:123), ...
    text = re.sub(r"\(cid:[0-9]+\)", " ", text)

    # Supprimer certains diacritiques / accents bizarres utilisés dans les équations
    text = text.replace("ˆ", "")

    # Normaliser les espaces
    text = re.sub(r"[ \t]+", " ", text)

    return text


def _remove_obvious_noise_lines(lines: List[str]) -> List[str]:
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            cleaned.append("")
            continue

        # 0) Petites lignes numériques ou symboliques -> bruit
        if len(s) <= 3 and re.fullmatch(r"[0-9\W]+", s):
            continue

        # 1) Lignes d'une seule lettre (ou 2) -> typiquement du bruit comme "c", "e", "D"
        if len(s) <= 2 and s.isalpha():
            continue

        letters = sum(ch.isalpha() for ch in s)

        # 2) Ligne du style "c e D" (lettres séparées par des espaces)
        if re.fullmatch(r"([A-Za-z]\s+){1,}[A-Za-z]", s):
            continue

        # 3) Plus d'espaces que de lettres -> probablement colonnes éclatées étranges
        if s.count(" ") > letters and letters < 10:
            continue

        # 4) Très peu de lettres par rapport à la longueur -> bruit visuel
        if letters / max(len(s), 1) < 0.25 and len(s) < 40:
            continue

        # 5) Lignes qui ressemblent à une ligne de tableau :
        #    - beaucoup de "colonnes" séparées par au moins 2 espaces
        #    - PAS de vraie ponctuation de phrase (.?!;:)
        chunks = re.split(r"\s{2,}", s)
        if len(chunks) >= 3 and not re.search(r"[\.!?;:]", s):
            # ex : "2018, 2023   Assembly/Real   Ego   1   MR"
            continue

        # 6) Lignes "surtout maths" (équations cassées)
        math_symbols = "=+-−*/<>≤≥∑∏∫()[]{}_^%|,:;"
        math_like = sum(ch.isdigit() or ch in math_symbols for ch in s)

        # 6.a) Lignes courtes bourrées de symboles, sans ponctuation de phrase
        if len(s) < 15 and math_like > 0 and not re.search(r"[\.!?]", s):
            # Exemple : "i }Nk", "k=1", "EDA =", "i=1 1{m(k"
            continue

        # 6.b) Lignes plus longues mais avec une forte proportion de symboles
        if math_like > 0 and math_like / len(s) > 0.4 and not re.search(r"[\.!?]", s):
            # On pourrait ici remplacer par "[EQUATION]" si tu veux garder une trace :
            # cleaned.append("[EQUATION]")
            # continue
            continue

        cleaned.append(s)

    return cleaned


def _remove_repeated_headers(lines: List[str]) -> List[str]:
    """
    Supprime headers/footers qui se répètent (titre d’article, nom de revue…)
    On garde la 1ère occurrence et on drop les suivantes.
    """
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
            and s.upper() == s  # tout en majuscules → très probablement header
        ):
            # garder une seule fois max
            if s in seen:
                continue
            seen.add(s)

        out.append(s)

    return out


def _merge_lines_into_paragraphs(lines: List[str]) -> str:
    """
    Recolle les lignes en paragraphes, avec gestion des mots coupés par un '-'.
    Une ligne vide => nouveau paragraphe.
    """
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
            # fin de paragraphe
            flush_buffer()
            continue

        if buffer:
            # gestion des coupures de mots : "inter-" + "\n" + "esting"
            prev = buffer[-1]
            if prev.endswith("-") and not prev.endswith("--"):
                # on fusionne sans espace : "inter-" + "esting" -> "interesting"
                buffer[-1] = prev[:-1] + s
            else:
                buffer.append(s)
        else:
            buffer.append(s)

    flush_buffer()

    # supprime les espaces multiples à l'intérieur des paragraphes
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()]

    return "\n\n".join(paragraphs)


def clean_raw_text(raw_text: str) -> str:
    """
    Pipeline complet de nettoyage.
    Utilisation :
        cleaned = clean_raw_text(doc.raw_text)
    """
    if not raw_text:
        return ""

    # 0) Normalisation des sauts de ligne
    text = _normalize_newlines(raw_text)

    # 1) Nettoyage des artefacts PDF (cid:80, ˆ, etc.)
    text = _remove_pdf_artifacts(text)

    # 2) Découpage en lignes
    lines = text.split("\n")

    # 3) virer les lignes clairement bruitées / math / tableaux
    lines = _remove_obvious_noise_lines(lines)

    # 4) retirer headers/footers répétés (titre de l'article, etc.)
    lines = _remove_repeated_headers(lines)

    # 5) recoller en paragraphes propres
    cleaned = _merge_lines_into_paragraphs(lines)

    return cleaned.strip()
