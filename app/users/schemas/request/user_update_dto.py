from pydantic import BaseModel, Field


class UserUpdateDto(BaseModel):
    username: str | None = Field(None)
    name: str | None = Field(None, max_length=150)
