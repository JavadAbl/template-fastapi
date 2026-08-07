from typing import Literal, Optional
from pydantic import BaseModel, Field


class GetManyQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, alias="pageSize", ge=2)
    sort_by: Optional[str] = Field(default=None, alias="sortBy")
    sort_order: Literal["asc", "desc"] = Field(
        default="asc", alias="sortOrder")
    search: Optional[str] = None

    model_config = {
        # Allows populating by field name (snake_case) OR alias (camelCase)
        "populate_by_name": True,
    }
