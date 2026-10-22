from ninja.errors import HttpError

from .schemas import ErrorResponse


def raise_api_error(
    status_code: int,
    message: str,
    details: dict[str, str] | None = None,
):
    raise HttpError(
        status_code,
        ErrorResponse(
            message=message,
            details=details,
        ).model_dump(),
    )