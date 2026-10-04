import os
import secrets
import smtplib
from email.message import EmailMessage

import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "development-secret-change-me")
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
RESET_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def generate_reset_token() -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    return token, expires

def smtp_is_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASS"))

def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Sends the reset link by email. Returns False (without raising) when
    SMTP isn't configured or sending fails, so the caller can fall back to
    the dev-mode response instead of crashing the request."""
    if not smtp_is_configured():
        return False

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user)

    message = EmailMessage()
    message["Subject"] = "Reset your VolunteerConnect password"
    message["From"] = sender
    message["To"] = to_email
    message.set_content(
        "We received a request to reset your VolunteerConnect password.\n\n"
        f"Reset it here (valid for {RESET_TOKEN_EXPIRE_MINUTES} minutes):\n{reset_link}\n\n"
        "If you didn't request this, you can ignore this email."
    )

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(message)
        return True
    except Exception:
        return False
