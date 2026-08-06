

from fastapi import APIRouter, status
from app.users.dependencies import UserServiceDep
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.response.user_dto import UserDto


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserDto, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateDto, service: UserServiceDep):
    return await service.create_user(user_data)


@router.get("/{user_id}", response_model=UserDto | None)
async def get_user(user_id: int, service: UserServiceDep):
    return await service.get_user_by_id(user_id)


@router.get("/")
async def get_users(service: UserServiceDep):
    return await service.get_users()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, service: UserServiceDep):
    return await service.delete_user_by_id(user_id)
