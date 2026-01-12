from fastapi import APIRouter, UploadFile, File,Depends
import shutil, os
from backend.app.core.deps import get_current_user
from backend.app.documents.pdf_utils import extract_text
from backend.app.rag.embeddings import embed_texts
from backend.app.rag.vector_store import add_chunks
from backend.app.rag.vector_store import debug_count
debug_count()


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
Depends(get_current_user)


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text (PDF or DOCX)
    pages = extract_text(path)

    chunks = []
    for page in pages:
        for i in range(0, len(page), 500):
            chunk = page[i:i + 500].strip()
            if chunk and len(chunk) > 30:
                chunks.append(chunk)

    if not chunks:
        print("❌ No chunks created from document")
        return {"error": "No readable text found in document"}

    print("🧩 FIRST CHUNK PREVIEW:", repr(chunks[0][:200]))

    embeddings = embed_texts(chunks)
    print("DEBUG chunks:", len(chunks))
    print("DEBUG embeddings:", len(embeddings))

    metadatas = [{"source": file.filename} for _ in chunks]

    add_chunks(chunks, embeddings, metadatas)

    return {
        "message": "Document processed successfully",
        "chunks": len(chunks)
    }
