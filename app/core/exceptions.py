from typing import Any
from uuid import UUID


class CustomBaseException(Exception):
    def __init__(
        self, error_code: str, message: str, extras: dict[str, Any] | None = None
    ) -> None:
        self.extras = extras
        self.error_code = error_code
        self.message = message
        super().__init__(message)

    def to_json(self) -> dict[str, Any]:
        serialized_extras = {
            key: str(value) if isinstance(value, UUID) else value
            for key, value in (self.extras or {}).items()
        }
        return {
            "error_code": self.error_code,
            "message": self.message,
            "extras": serialized_extras,
        }


class ResourceNotFoundException(CustomBaseException):
    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        extras: dict[str, Any] | None = None,
    ):
        if error_code is None:
            error_code = "RESOURCE_NOT_FOUND"
        if message is None:
            message = "Resource not found"
        super().__init__(error_code, message, extras)


class InvalidStateException(CustomBaseException):
    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        extras: dict[str, Any] | None = None,
    ):
        if error_code is None:
            error_code = "INVALID_STATE"
        if message is None:
            message = "Invalid resource state"
        super().__init__(error_code, message, extras)


class InvalidInputException(CustomBaseException):
    def __init__(
        self,
        message: str | None = "Invalid input",
        error_code: str | None = "INVALID_INPUT",
        extras: dict[str, Any] | None = None,
    ):
        super().__init__(error_code, message, extras)


class AccessDeniedException(CustomBaseException):
    def __init__(
        self,
        message: str = "User does not have permission to access this resource",
        error_code: str = "ACCESS_DENIED",
        extras: dict[str, Any] | None = None,
    ):
        super().__init__(error_code, message, extras)


class UnexpectedErrorException(CustomBaseException):
    def __init__(
        self,
        message: str | None = "An unexpected error occurred",
        error_code: str | None = "UNEXPECTED_ERROR",
        extras: dict[str, Any] | None = None,
    ):
        super().__init__(error_code, message, extras)
