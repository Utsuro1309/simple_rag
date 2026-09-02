import io
import logging
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from app.utils.chunking import semantic_chunking

logger = logging.getLogger(__name__)

def extract_text_from_pdf_safe(file_bytes: bytes) -> Optional[str]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if not text.strip():
            logger.warning("PDF is scanned or contains no extractable text.")
            return None
        return text
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}")
        return None

def process_small_document(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf_safe(file_bytes)
    else:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            logger.error(f"Cannot decode file {filename} as UTF-8.")
            return []
    if not text:
        return []
    chunks = semantic_chunking(text)
    return [{
        "content": chunk["text"],
        "source_file": filename,
        "doc_type": "small",
        "token_count": chunk["token_count"]
    } for chunk in chunks]

def process_large_document_by_page(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            pages.append({
                "content": text,
                "source_file": filename,
                "doc_type": "large",
                "page_number": i+1
            })
    return pages