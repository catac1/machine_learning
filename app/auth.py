import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

# Distinct secret keys for security
ACCESS_SECRET = "your-access-token-secret-key"
REFRESH_SECRET = "your-refresh-token-secret-key"
ALGORITHM = "HS256"


# Pure bcrypt (No passlib needed)
def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# Pure PyJWT (No python-jose needed)
def create_access_token(
    user_email: str, expires_delta: timedelta = timedelta(minutes=15)
):
    payload = {"sub": user_email, "exp": expires_delta}
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_email: str) -> str:
    """Generates a long-lived 7-day refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=7)

    payload = {
        "sub": str(user_email),
        "exp": expire,
        "type": "refresh",  # Explicitly flag token type
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm=ALGORITHM)
