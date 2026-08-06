from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.exceptions import ConflictException, NotFoundException

# Define generic type variables
ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_one(
        self, *filters: Any, **filter_by: Any
    ) -> ModelType | None:
        """Fetch a single record matching the given criteria."""
        statement = select(self.model)
        if filters:
            statement = statement.where(*filters)
        if filter_by:
            statement = statement.filter_by(**filter_by)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def create(self, payload: CreateSchemaType) -> ModelType:
        db_obj = self.model.model_validate(payload)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, payload: UpdateSchemaType) -> ModelType:
        """Update an existing database record.

        Args:
            db_obj: The existing database object to update.
            payload: The Pydantic/SQLModel schema containing the new data.

        Returns:
            The updated database object.
        """
        # exclude_unset=True ensures that fields not explicitly provided
        # in the payload are NOT overwritten with None (supports partial updates / PATCH)

        db_obj = await self.get_and_check_exists(id)
        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_obj, key, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> None:
        obj = await self.get_by_id(id)
        if not obj:
            raise NotFoundException(
                f"{self.model.__name__} with id {id} not found")

        await self.session.delete(obj)
        await self.session.commit()

    async def get_and_check_exists(
        self, *filters: Any, **filter_by: Any
    ) -> ModelType:
        entity = await self.get_one(*filters, **filter_by)

        if entity is None:
            raise NotFoundException()

        return entity

    async def check_duplicate(
        self, *filters: Any, **filter_by: Any
    ) -> None:
        entity = await self.get_one(*filters, **filter_by)

        if entity is not None:
            raise ConflictException()
