from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel
from sqlmodel import SQLModel, String, asc, desc, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.exceptions import ConflictException, NotFoundException
from app.contracts.schemas.request.get_many_query_dto import GetManyQuery

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
DtoType = TypeVar("DtoType", bound=BaseModel)


class BaseRepository(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, DtoType]
):
    model: Type[ModelType]
    dto_model: Type[DtoType]

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _get_columns_for_dto(self, dto_class: Type[DtoType]) -> list[Any]:
        """Resolve DTO fields to SQLAlchemy columns."""
        cols = []
        for field_name in dto_class.model_fields:
            if hasattr(self.model, field_name):
                cols.append(getattr(self.model, field_name))
        return cols

    def _apply_search(
        self,
        stmt,
        query: GetManyQuery,
        search_fields: list[str],
    ):
        search = (query.search or "").strip()

        if not search or not search_fields:
            return stmt

        mapper = inspect(self.model)
        filters = []
        term = f"%{search}%"

        for field in search_fields:
            # Only allow real DB columns
            if field not in mapper.columns:
                continue

            column = mapper.columns[field]

            # Only apply ILIKE to string-like columns
            if isinstance(column.type, String):
                filters.append(
                    getattr(self.model, field).ilike(term)
                )

        if filters:
            stmt = stmt.where(or_(*filters))

        return stmt

    def _apply_sort(self, stmt, query: GetManyQuery):
        mapper = inspect(self.model)

        if query.sort_by and query.sort_by in mapper.columns:
            sort_column = getattr(self.model, query.sort_by)

            if query.sort_order == "desc":
                stmt = stmt.order_by(desc(sort_column))
            else:
                stmt = stmt.order_by(asc(sort_column))
        else:
            # Stable fallback ordering, useful for pagination
            primary_key = mapper.primary_key
            if primary_key:
                stmt = stmt.order_by(*primary_key)

        return stmt

    def _apply_pagination(self, stmt, query: GetManyQuery):
        offset = (query.page - 1) * query.page_size
        return stmt.offset(offset).limit(query.page_size)

    # ------------------------------------------------------------------ #
    # Existing methods (unchanged)
    # ------------------------------------------------------------------ #
    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        query: GetManyQuery,
        searchFields: list[str],
    ) -> list[ModelType]:
        stmt = select(self.model)

        stmt = self._apply_search(stmt, query, searchFields)
        stmt = self._apply_sort(stmt, query)
        stmt = self._apply_pagination(stmt, query)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_one(
        self, *filters: Any, **filter_by: Any
    ) -> ModelType | None:
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

    async def update(
        self, id: int, payload: UpdateSchemaType
    ) -> ModelType:
        db_obj = await self.get_and_check_exists(id=id)
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
                f"{self.model.__name__} with id {id} not found"
            )
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

    # ------------------------------------------------------------------ #
    # DTO projection methods
    # ------------------------------------------------------------------ #
    async def get_all_dtos(
        self,
        query: GetManyQuery,
        searchFields: list[str],
        *,
        dto_class: Type[DtoType] | None = None,
    ) -> list[DtoType]:
        """
        Fetch multiple records as DTOs.
        Uses default DTO unless dto_class is provided.
        """
        target_dto = dto_class or self.dto_model

        cols = self._get_columns_for_dto(target_dto)

        stmt = select(*cols)

        stmt = self._apply_search(stmt, query, searchFields)
        stmt = self._apply_sort(stmt, query)
        stmt = self._apply_pagination(stmt, query)

        result = await self.session.execute(stmt)

        return [
            target_dto.model_validate(row)
            for row in result.mappings().all()
        ]

    async def get_one_dto(
        self,
        *filters: Any,
        dto_class: Type[DtoType] | None = None,
        **filter_by: Any
    ) -> DtoType | None:
        """Fetch a single record. Uses default DTO unless dto_class is provided."""
        target_dto = dto_class or self.dto_model
        cols = self._get_columns_for_dto(target_dto)

        statement = select(*cols)
        if filters:
            statement = statement.where(*filters)
        if filter_by:
            statement = statement.filter_by(**filter_by)

        result = await self.session.execute(statement)
        row = result.first()
        return target_dto.model_validate(row._mapping) if row else None

    async def get_by_id_dto(
        self,
        id: int,
        *,
        dto_class: Type[DtoType] | None = None
    ) -> DtoType | None:
        target_dto = dto_class if dto_class is not None else self.dto_model
        cols = self._get_columns_for_dto(target_dto)

        # Dynamically get the primary key column of the model
        mapper = inspect(self.model)
        pk_col = mapper.primary_key[0]

        statement = select(*cols).where(pk_col == id)

        result = await self.session.execute(statement)
        row = result.first()
        return target_dto.model_validate(row._mapping) if row else None

    async def get_dto_and_check_exists(
        self,
        *filters: Any,
        dto_class: Type[DtoType] | None = None,
        **filter_by: Any
    ) -> DtoType:
        """Fetch or raise 404. Uses default DTO unless dto_class is provided."""
        dto = await self.get_one_dto(*filters, dto_class=dto_class, **filter_by)
        if dto is None:
            raise NotFoundException()
        return dto
