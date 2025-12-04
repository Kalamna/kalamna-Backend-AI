import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:  # i have no idea what could happen if this is not set
    raise ValueError("JWT_SECRET environment variable must be set")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=7)

ISSUER = "kalamna_services"


def _ts(dt: datetime) -> int:
    """Convert datetime to UNIX timestamp."""
    return int(dt.timestamp())


def create_access_token(employee_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": employee_id,
        "role": role,
        "jti": str(uuid4()),
        "iat": _ts(now),
        "exp": _ts(now + ACCESS_TTL),
        "iss": ISSUER,
        "aud": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(employee_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": employee_id,
        "jti": str(uuid4()),
        "iat": _ts(now),
        "exp": _ts(now + REFRESH_TTL),
        "iss": ISSUER,
        "aud": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str, audience: str = None) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer=ISSUER,
            audience=audience,
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        raise Exception("Token has expired") from err
    except jwt.InvalidTokenError as err:
        raise Exception("Invalid token") from err


# password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)  # setup password hashing schema with bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Returns the hashed password>> string output.
    """
    return pwd_context.hash(password)  # hash given password


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a stored bcrypt hash.
    Use this during login. >> boolen output
    """
    return pwd_context.verify(plain, hashed)
