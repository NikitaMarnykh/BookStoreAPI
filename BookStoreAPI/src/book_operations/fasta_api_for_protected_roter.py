from fastapi_users import FastAPIUsers, fastapi_users

from src.auth.auth import auth_backend
from src.auth.manager import get_user_manager
from src.auth.models_user import User


# Для текущего пользователя
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
