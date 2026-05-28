import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.config import UPLOAD_DIR
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserLogin, UserResponse, UserUpdate, Token
from app.services.auth_service import register, authenticate, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


class BuyerRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=6, max_length=50)


class SellerRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=6, max_length=50)
    shop_name: str = Field(min_length=2, max_length=100)


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


@router.post("/register", response_model=Token)
def buyer_register(data: BuyerRegister, db: Session = Depends(get_db)):
    try:
        user = register(db, data.username, data.email, data.password, role="buyer")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/register/seller", response_model=Token)
def seller_register(data: SellerRegister, db: Session = Depends(get_db)):
    try:
        user = register(db, data.username, data.email, data.password, role="seller", shop_name=data.shop_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def user_login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate(db, data.username, data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.email is not None:
        current_user.email = data.email
    if data.avatar is not None:
        current_user.avatar = data.avatar
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"detail": "密码修改成功"}


@router.post("/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or ".jpg")[1]
    filename = f"avatar_{uuid.uuid4().hex}{ext}"
    filepath = Path(UPLOAD_DIR) / filename
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    current_user.avatar = f"/uploads/{filename}"
    db.commit()
    db.refresh(current_user)
    return {"url": current_user.avatar}
