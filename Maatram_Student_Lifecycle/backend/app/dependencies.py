from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token
bearer = HTTPBearer(auto_error=False)
def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(401, "Authentication required")
    payload = decode_token(credentials.credentials)
    if not payload: raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active: raise HTTPException(401, "Account unavailable")
    return user
def require_roles(*roles):
    def check(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, "Insufficient permissions")
        return user
    return check
