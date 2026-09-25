from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import authenticate_user
from app.config import password_meets_policy
from app.db import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserProfile
from app.security import create_access_token, get_current_api_user

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.post("/login", response_model=LoginResponse)
def api_login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    ok, policy_msg = password_meets_policy(body.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=policy_msg)
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )
    token = create_access_token(user.email)
    return LoginResponse(
        access_token=token,
        email=user.email,
        display_name=user.display_name,
    )


@router.get("/me", response_model=UserProfile)
def api_me(current: User = Depends(get_current_api_user)) -> UserProfile:
    return UserProfile(email=current.email, display_name=current.display_name)


@router.post("/logout")
def api_logout(_current: User = Depends(get_current_api_user)) -> dict[str, str]:
    return {"status": "ok", "message": "Cierra sesión en el cliente eliminando el token."}
