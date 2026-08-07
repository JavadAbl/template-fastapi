from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.base_repository import BaseRepository
from app.users.models.user import User
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.request.user_update_dto import UserUpdateDto
from app.users.schemas.response.user_dto import UserDto


class UserRepository(BaseRepository[User, UserCreateDto, UserUpdateDto, UserDto]):
    model = User
    dto_model = UserDto

    def __init__(self, session: AsyncSession):
        super().__init__(session)
