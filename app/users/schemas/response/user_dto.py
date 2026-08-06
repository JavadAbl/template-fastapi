from pydantic import BaseModel


class UserDto(BaseModel):
    id: int
    username: str
    name: str | None = None

    model_config = {"from_attributes": True}
