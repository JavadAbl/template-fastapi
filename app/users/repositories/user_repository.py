from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.base_repository import BaseRepository
from app.users.models.user import User
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.request.user_update_dto import UserUpdateDto


class UserRepository(BaseRepository[User, UserCreateDto, UserUpdateDto]):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)
