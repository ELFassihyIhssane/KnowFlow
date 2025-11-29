from sqlalchemy.orm import Session
from ..memory.document_store import Document
from ..external.pdf_extractor import extract_text_from_pdf_url


def process_pdf_for_document(db: Session, doc: Document):
    """Télécharge et extrait le texte d’un document PDF."""
    if not doc.pdf_url:
        return False
    
    text = extract_text_from_pdf_url(doc.pdf_url)
    if not text:
        return False

    doc.raw_text = text
    db.add(doc)
    db.commit()
    return True


def process_all_documents(db: Session, limit: int = None):
    """Traite tous les documents sans texte."""
    query = db.query(Document).filter(Document.raw_text == None)

    if limit:
        query = query.limit(limit)

    docs = query.all()

    processed = 0
    for doc in docs:
        ok = process_pdf_for_document(db, doc)
        if ok:
            processed += 1

    return processed
