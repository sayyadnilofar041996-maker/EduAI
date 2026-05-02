from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# PASSWORD HASHING
# ─────────────────────────────────────────────

# CryptContext sets up bcrypt as our hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Takes a plain password, returns a bcrypt hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain password matches a stored hash. Returns True or False."""
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────
# JWT TOKEN
# ─────────────────────────────────────────────

SECRET_KEY  = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM   = "HS256"       # hashing algorithm for JWT
TOKEN_EXPIRY = 60 * 24      # token valid for 24 hours (in minutes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token.
    data = dictionary of info to encode (e.g. user id, role)
    expires_delta = how long until token expires
    """
    to_encode = data.copy()

    # Set expiry time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY)

    to_encode.update({"exp": expire})

    # Encode everything into a JWT string
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT token and returns the data inside.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None