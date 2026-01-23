from datetime import datetime
import random
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.db.models.user import User
from backend.app.db.models.otp import OTP
from backend.app.auth.schemas import UserCreate, UserLogin, OTPVerify
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from backend.app.core.email import send_otp_email


# ---------------- REGISTER ----------------
def register_service(db, data: UserCreate):
    email = data.email.strip().lower()

    existing_user = db.query(User).filter(User.email == email).first()

    # Case 1: User already exists and is verified
    if existing_user and existing_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Case 2: User exists but NOT verified → resend OTP
    if existing_user and not existing_user.is_verified:
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


# ---------------- VERIFY OTP ----------------
def verify_otp_service(db, data: OTPVerify):
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


# ---------------- LOGIN ----------------
def login_service(db, data: UserLogin):
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


# ---------------- RESEND OTP ----------------
def resend_otp_service(db, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_verified:
        raise HTTPException(400, "Email already verified")

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
    return {"message": "OTP resent successfully"}


def forgot_password_service(db: Session, email: str):
    email = email.strip().lower()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

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

    return {"message": "Password reset OTP sent to your email"}


def reset_password_service(db: Session, email: str, otp: str, new_password: str):
    email = email.strip().lower()

    otp_record = db.query(OTP).filter(
        OTP.email == email,
        OTP.code == otp,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if not otp_record:
        raise HTTPException(400, "Invalid or expired OTP")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.hashed_password = hash_password(new_password)

    db.delete(otp_record)
    db.commit()

    return {"message": "Password reset successful"}
