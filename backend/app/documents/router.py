from fastapi import APIRouter, UploadFile, File, Depends

from backend.app.core.deps import get_current_user
from backend.app.documents.service  import process_uploaded_document

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    return process_uploaded_document(file)
