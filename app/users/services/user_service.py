# app/services/user.py

from app.users.models.user import User
from app.users.repositories.user_repository import UserRepository
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.request.user_update_dto import UserUpdateDto
from app.users.schemas.response.user_dto import UserDto


class UserService():

    user_rep: UserRepository

    def __init__(self, user_rep: UserRepository):
        self.user_rep = user_rep

    async def get_users(self) -> list[User]:
        return await self.user_rep.get_all()

    async def get_user_by_id(self, id: int) -> User | None:
        return await self.user_rep.get_and_check_exists(id=id)

    async def create_user(self, payload: UserCreateDto) -> UserDto:
        await self.user_rep.check_duplicate(username=payload.username)

        # Use inherited base CRUD method
        saved_user = await self.user_rep.create(payload)

        # Convert entity to response DTO
        return UserDto.model_validate(saved_user)

    async def update_user_by_id(self, id: int, payload: UserUpdateDto) -> User | None:
        await self.user_rep.get_and_check_exists(username=payload.username)
        await self.user_rep.update(id, payload)

    async def delete_user_by_id(self, id: int) -> User | None:
        return await self.user_rep.delete(id)
