

from fastapi import APIRouter, Depends, Query, status
from app.contracts.schemas.request.get_many_query_dto import GetManyQuery
from app.users.dependencies import UserServiceDep
from app.users.schemas.request.user_create_dto import UserCreateDto
from app.users.schemas.request.user_update_dto import UserUpdateDto
from app.users.schemas.response.user_dto import UserDto


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}",)
async def get_user(user_id: int, service: UserServiceDep):
    return await service.get_user_by_id(user_id)


@router.get("/")
async def get_users(service: UserServiceDep, query: GetManyQuery = Query(), ):
    return await service.get_users(query)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateDto, service: UserServiceDep):
    return await service.create_user(user_data)


@router.patch("/{user_id}")
async def update_user(user_id: int, payload: UserUpdateDto, service: UserServiceDep):
    return await service.update_user_by_id(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, service: UserServiceDep):
    return await service.delete_user_by_id(user_id)
