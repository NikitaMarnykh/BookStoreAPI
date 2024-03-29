from fastapi import FastAPI
from fastapi_users import FastAPIUsers, fastapi_users

from src.auth.models_user import User
from src.auth.manager import get_user_manager
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.auth.auth import auth_backend
from src.book_operations.router import router as books_router

app = FastAPI(title="BookStoreAPI")
#

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate),
                   prefix="/users",
                   tags=["users"])

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(books_router)
