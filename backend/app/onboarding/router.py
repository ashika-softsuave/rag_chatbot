from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.db.models.user import User

from backend.app.onboarding.schemas import (
    OnboardingStartResponse,
    OnboardingNextRequest
)

from backend.app.onboarding.service import (
    start_onboarding_service,
    onboarding_next_service,
    reset_onboarding_service, get_or_create_employee
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


#START ONBOARDING
@router.post("/start", response_model=OnboardingStartResponse)
def start_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return start_onboarding_service(db, current_user)


# NEXT STEP
@router.post("/next")
def onboarding_next(
    req: OnboardingNextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return onboarding_next_service(db, current_user, req.user_input)


#  RESET
@router.post("/reset")
def reset_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return reset_onboarding_service(db, current_user)

# backend/app/onboarding/router.py
@router.post("/onboarding/reset")
def reset_onboarding(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = get_or_create_employee(db, current_user)
    employee.onboarding_state = {
        "active": False,
        "paused": False,
        "step_index": 0,
        "data": {},
        "completed": False
    }
    db.commit()
    return {"status": "reset"}
