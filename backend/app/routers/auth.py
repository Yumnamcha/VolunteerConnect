import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import User
from ..schemas import (
    UserRegister, LoginRequest, TokenResponse, UserOut,
    ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest
)
from ..security import (
    hash_password, verify_password, create_access_token,
    generate_reset_token, send_password_reset_email, smtp_is_configured
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

MAX_DOCUMENT_LENGTH = 2_800_000  # roughly 2MB once base64-decoded

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if data.role not in ["volunteer", "coordinator"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    document = data.verification_document
    if document and len(document) > MAX_DOCUMENT_LENGTH:
        raise HTTPException(status_code=400, detail="Verification file is too large (max 2MB)")

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role=data.role,
        verification_document=document,
        verification_status="pending" if document else "unverified"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user
    }

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    generic_message = "If that email is registered, a reset link has been sent."
    user = db.query(User).filter(User.email == data.email.lower()).first()

    # Always return the same message whether or not the email exists, so this
    # endpoint can't be used to check which emails are registered.
    if not user:
        return {"message": generic_message, "dev_reset_token": None}

    token, expires = generate_reset_token()
    user.reset_token = token
    user.reset_token_expires = expires
    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    reset_link = f"{frontend_url}/reset-password?token={token}"
    emailed = send_password_reset_email(user.email, reset_link)

    return {
        "message": generic_message,
        "dev_reset_token": None if emailed or smtp_is_configured() else token
    }

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password updated. You can now sign in."}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user
    }
