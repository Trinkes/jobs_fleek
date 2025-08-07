from typing import Any

from app.logs.json_serializable import make_json_serializable


class CustomBaseException(Exception):
    def __init__(
        self, error_code: str, message: str, extras: dict[str, Any] | None = None
    ) -> None:
        self.extras = extras
        self.error_code = error_code
        self.message = message
        super().__init__(message)

    def to_json(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "extras": make_json_serializable(self.extras),
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
