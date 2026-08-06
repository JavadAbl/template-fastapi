from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a requested user cannot be found."""

    def __init__(self, identifier: str = "entity") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{identifier} not found.",
        )


class ConflictException(HTTPException):
    """Raised when a requested user cannot be found."""

    def __init__(self, identifier: str = "entity") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{identifier} already exists.",
        )
