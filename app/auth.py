from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_access_token(user_id, email):
    exp = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": str(user_id), "email": email, "exp": exp},
                      settings.secret_key, algorithm="HS256")

def get_current_user(token=Depends(oauth2_scheme)):
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        uid = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise error
    c = get_connection()
    user = c.execute(
        "SELECT id,email,name,created_at FROM users WHERE id=?", (uid,)
    ).fetchone()
    c.close()
    if not user:
        raise error
    return dict(user)
