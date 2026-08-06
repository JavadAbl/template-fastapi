# app/dependencies.py
from typing import Annotated
from fastapi import Depends

from app.contracts.dependencies import SessionDep
from app.users.repositories.user_repository import UserRepository
from app.users.services.user_service import UserService


# 2. Inject Repository


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]

# 3. Inject Service (Injects the Repository automatically!)


def get_user_service(repo: UserRepoDep) -> UserService:
    return UserService(repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
