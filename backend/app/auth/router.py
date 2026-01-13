from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
from passlib.context import CryptContext
from backend.app.core.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.db.models.otp import OTP
from backend.app.auth.schemas import *
from backend.app.core.security import hash_password, verify_password, create_access_token
Depends(get_current_user)
from backend.app.auth.schemas import (
    UserCreate,
    UserLogin,
    Token,
    OTPVerify
)
from backend.app.core.email import send_otp_email


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.strip().lower()

    existing_user = db.query(User).filter(User.email == email).first()

    # Case 1: User already exists and is verified
    if existing_user and existing_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Case 2: User exists but NOT verified → resend OTP
    if existing_user and not existing_user.is_verified:
        # Remove old OTPs
        db.query(OTP).filter(OTP.email == email).delete()

        otp_code = str(random.randint(100000, 999999))
        db.add(
            OTP(
                email=email,
                code=otp_code,
                expires_at=OTP.expiry()
            )
        )
        db.commit()

        send_otp_email(email, otp_code)
        return {"message": "OTP resent to your email"}

    # Case 3: New user → create user + send OTP
    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        is_verified=False
    )

    db.add(user)
    db.commit()

    otp_code = str(random.randint(100000, 999999))
    db.add(
        OTP(
            email=email,
            code=otp_code,
            expires_at=OTP.expiry()
        )
    )
    db.commit()

    send_otp_email(email, otp_code)
    return {"message": "OTP sent to your email"}



@router.post("/verify-otp")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    otp = db.query(OTP).filter(
        OTP.email == data.email,
        OTP.code == data.code,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if not otp:
        raise HTTPException(400, "Invalid or expired OTP")

    user = db.query(User).filter(User.email == data.email).first()
    user.is_verified = True

    db.delete(otp)
    db.commit()

    return {"message": "Account verified"}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    if not user.is_verified:
        raise HTTPException(status_code=401, detail="Email not verified")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/resend-otp")
def resend_otp(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_verified:
        raise HTTPException(400, "Email already verified")

    # 🔥 Remove any old OTPs
    db.query(OTP).filter(OTP.email == email).delete()

    otp_code = str(random.randint(100000, 999999))
    db.add(OTP(
        email=email,
        code=otp_code,
        expires_at=OTP.expiry()
    ))
    db.commit()

    print("📧 OTP (dev mode):", otp_code)  # replace with email later
    return {"message": "OTP resent successfully"}
