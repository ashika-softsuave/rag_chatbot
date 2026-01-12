import fitz  # PyMuPDF
import re

def clean_text(text: str) -> str:
    # remove invisible & junk characters
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text

def extract_text(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        text = page.get_text()
        text = clean_text(text)
        if len(text) > 50:  # ✅ ignore useless pages
            pages.append(text)

    return pages
