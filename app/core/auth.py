from fastapi import HTTPException, Cookie, Depends
from typing import Optional

# Simple password-based authentication
SECRET_PASSWORD = "tt55oo77"

def verify_password(password: str) -> bool:
    """Verify if the provided password is correct"""
    return password == SECRET_PASSWORD

def check_auth(auth_token: Optional[str] = Cookie(None, alias="mirror_auth")) -> bool:
    """Check if user is authenticated via cookie"""
    return auth_token == SECRET_PASSWORD

def require_auth(auth_token: Optional[str] = Cookie(None, alias="mirror_auth")):
    """Dependency to require authentication"""
    if not check_auth(auth_token):
        raise HTTPException(status_code=401, detail="Authentication required")
    return True
