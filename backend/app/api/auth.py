from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User
from backend.app.models.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from backend.app.core.security import hash_password, verify_password, create_access_token, get_current_user_payload

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    new_user = User(
        email=payload.email.lower(),
        name=payload.name.strip(),
        hashed_password=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})
    response.set_cookie(
        key="truthlens_access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=new_user.id, email=new_user.email, name=new_user.name, role=new_user.role)
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    response.set_cookie(
        key="truthlens_access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, name=user.name, role=user.role)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    user_payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
):
    if not user_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    
    user = db.query(User).filter(User.id == user_payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return UserResponse(id=user.id, email=user.email, name=user.name, role=user.role)
