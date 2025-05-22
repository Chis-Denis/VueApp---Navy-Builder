from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from database.database import get_db
from database.models import User
from Backend.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    register_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from Backend.services.monitoring_service import log_activity
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_monitored: bool

    class Config:
        orm_mode = True

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    log_activity(
        db=db,
        user_id=user.id,
        action="CREATE",
        entity_type="user",
        entity_id=user.id,
        details="User registration"
    )
    return user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    log_activity(
        db=db,
        user_id=user.id,
        action="READ",
        entity_type="auth",
        entity_id=user.id,
        details="User login"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin/monitored-users", response_model=List[UserResponse])
async def get_monitored_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view monitored users"
        )
    
    monitored_users = db.query(User).filter(User.is_monitored == True).all()
    return monitored_users

@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all users"
        )
    users = db.query(User).all()
    return users

@router.post("/admin/users/{user_id}/toggle-monitoring")
async def toggle_monitoring(
    user_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to toggle monitoring"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_monitored = not user.is_monitored
    db.commit()
    db.refresh(user)
    return {"id": user.id, "is_monitored": user.is_monitored} 