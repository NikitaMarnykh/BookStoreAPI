from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from starlette.responses import Response

from src.auth.models_user import User
from src.database import get_user_db
from src.image.crud import delete_image

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
            print(f"User {user.id} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)

        return created_user

    async def delete(
        self,
        user: models.UP,
        request: Optional[Request] = None,
    ) -> None:

        await self.on_before_delete(user, request)
        await self.user_db.delete(user)
        for book in user.books:
            image_name = book.image.name
            await delete_image(image_name=image_name)
        await self.on_after_delete(user, request)

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        print(f"User {user.id} is logged in")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
