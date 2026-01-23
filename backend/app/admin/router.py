from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.admin.service import (
    seating_status_service,
    reset_seating_service
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.admin.schemas import SeatingConfigRequest
from backend.app.admin.service import configure_seating
from backend.app.db.session import get_db
# from backend.app.auth.dependencies import admin_required

router = APIRouter(prefix="/admin/seating", tags=["Admin Seating"])


@router.post("/seating/configure")
def configure_seats(
    req: SeatingConfigRequest,
    db: Session = Depends(get_db),
    # admin=Depends(admin_required)
):
    configure_seating(db, req.tech_stack.lower(), req.rows, req.columns)
    return {"status": "configured"}

@router.get("/status")
def seating_status(
        db: Session = Depends(get_db)
):
    return seating_status_service(db)


@router.post("/reset")
def reset_seating(
        db: Session = Depends(get_db)
):
    return reset_seating_service(db)

@router.get("/seating/status")
def get_seating_status(
    db: Session = Depends(get_db),
    # admin=Depends(admin_required)
):
    return seating_status(db)
