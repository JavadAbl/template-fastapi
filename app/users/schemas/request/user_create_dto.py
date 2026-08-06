from pydantic import BaseModel, Field


class UserCreateDto(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
    )

    name: str | None = Field(
        None,
    )

    password: str = Field(
        ...,
    )
