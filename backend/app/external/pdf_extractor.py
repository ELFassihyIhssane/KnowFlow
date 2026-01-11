import io
import requests
from pdfminer.high_level import extract_text

def download_pdf(pdf_url: str) -> bytes | None:
    try:
        response = requests.get(pdf_url, timeout=20)
        if response.status_code != 200:
            return None
        return response.content
    except Exception:
        return None


def extract_pdf_text(pdf_bytes: bytes) -> str | None:
    try:
        buffer = io.BytesIO(pdf_bytes)
        text = extract_text(buffer)
        if not text:
            return None

        cleaned = text.replace("\x00", "").strip()
        return cleaned or None
    except Exception:
        return None



def extract_text_from_pdf_url(pdf_url: str) -> str | None:
    pdf_bytes = download_pdf(pdf_url)
    if not pdf_bytes:
        return None

    return extract_pdf_text(pdf_bytes)
