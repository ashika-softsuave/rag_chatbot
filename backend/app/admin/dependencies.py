from fastapi import Depends, HTTPException
from backend.app.auth.dependencies import get_current_user
from backend.app.db.models.user import User
from backend.app.core.constants import ADMIN_EMAIL


def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin or current_user.email != ADMIN_EMAIL:
        raise HTTPException(
            status_code=403,
            detail="Admin access only"
        )
    return current_user
