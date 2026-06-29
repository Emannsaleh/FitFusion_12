from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from App.database import SessionLocal
from App.schemas import RegisterRequest, LoginRequest
from App.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    hash_password
)
from App.Models.User import User
router = APIRouter()

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- REGISTER ----------------
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    hashed_pw = hash_password(request.password)
    user = create_user(db, request.username, request.email, hashed_pw)

    return {
        "message": "User created successfully",
        "user_id": user.id
    }


# ---------------- LOGIN ----------------
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }


# ---------------- ME (بدون Auth) ----------------
@router.get("/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }