from fastapi import Depends, HTTPException, status
from backend.app.auth.jwt import verify_access_token
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from backend.app.db.models.user import User


def get_current_user(
    token: str = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
