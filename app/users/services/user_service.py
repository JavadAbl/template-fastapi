# app/services/user.py

from app.contracts.schemas.request.get_many_query_dto import GetManyQuery
from app.users.models.user import User
from app.users.repositories.user_repository import UserRepository
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.request.user_update_dto import UserUpdateDto
from app.users.schemas.response.user_dto import UserDto


class UserService():

    user_rep: UserRepository

    def __init__(self, user_rep: UserRepository):
        self.user_rep = user_rep

    async def get_users(self, query: GetManyQuery) -> list[UserDto]:
        return await self.user_rep.get_all_dtos(query, ["username"])

    async def get_user_by_id(self, id: int) -> UserDto | None:
        return await self.user_rep.get_dto_and_check_exists(id=id)

    async def create_user(self, payload: UserCreateDto) -> int:
        await self.user_rep.check_duplicate(username=payload.username)

        # Use inherited base CRUD method
        saved_user = await self.user_rep.create(payload)

        # Convert entity to response DTO
        return saved_user.id

    async def update_user_by_id(self, id: int, payload: UserUpdateDto) -> None:
        await self.user_rep.update(id, payload)

    async def delete_user_by_id(self, id: int) -> None:
        return await self.user_rep.delete(id)
