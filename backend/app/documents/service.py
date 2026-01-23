import os
import shutil
from fastapi import UploadFile

from backend.app.documents.pdf_utils import extract_text
from backend.app.rag.embeddings import embed_texts
from backend.app.rag.vector_store import add_chunks

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_uploaded_document(file: UploadFile) -> dict:
    path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    pages = extract_text(path)

    chunks = []
    for page in pages:
        for i in range(0, len(page), 500):
            chunk = page[i:i + 500].strip()
            if chunk and len(chunk) > 30:
                chunks.append(chunk)

    if not chunks:
        return {"error": "No readable text found in document"}

    embeddings = embed_texts(chunks)
    metadatas = [{"source": file.filename} for _ in chunks]

    add_chunks(chunks, embeddings, metadatas)

    return {
        "message": "Document processed successfully",
        "chunks": len(chunks)
    }
