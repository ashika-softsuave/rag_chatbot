from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.auth.schemas import (
    UserCreate,
    UserLogin,
    OTPVerify,
    Token
)
from backend.app.auth.service import (
    register_service,
    verify_otp_service,
    login_service,
    resend_otp_service
)
from backend.app.auth.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from backend.app.auth.service import (
    forgot_password_service,
    reset_password_service
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    return register_service(db, data)


@router.post("/verify-otp")
def verify_otp(
    data: OTPVerify,
    db: Session = Depends(get_db)
):
    return verify_otp_service(db, data)


@router.post("/login", response_model=Token)
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    return login_service(db, data)


@router.post("/resend-otp")
def resend_otp(
    email: str,
    db: Session = Depends(get_db)
):
    return resend_otp_service(db, email)


@router.post("/forgot-password")
def forgot_password(
    req: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    return forgot_password_service(db, req.email)

@router.post("/reset-password")
def reset_password(
    req: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return reset_password_service(
        db,
        req.email,
        req.otp,
        req.new_password
    )

