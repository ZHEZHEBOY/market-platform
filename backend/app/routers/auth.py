from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, UserUpdate, Token
from app.services.auth_service import register, authenticate, create_access_token

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


@router.post("/register", response_model=Token)
def user_register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = register(db, data)
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
