from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings
pwd = CryptContext(schemes=["argon2"], deprecated="auto")
ALGORITHM = "HS256"
def hash_password(password: str) -> str: return pwd.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd.verify(password, hashed)
def create_token(user_id: int, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "role": role, "exp": exp}, settings.JWT_SECRET, algorithm=ALGORITHM)
def decode_token(token: str):
    try: return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError: return None
