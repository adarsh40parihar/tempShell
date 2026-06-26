from fastapi import APIRouter, Depends

from models.user import UserCreate, UserLogin, Token
from utils.security import get_current_user
import controllers.auth_controller as auth_controller

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", status_code=201)
async def signup(user: UserCreate):
    return auth_controller.signup(user)


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    return auth_controller.login(user)


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return auth_controller.get_me(current_user["username"])
