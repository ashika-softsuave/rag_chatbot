from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from backend.app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    return payload["sub"]
