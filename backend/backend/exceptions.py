from typing import Any


class APIException(Exception):
    status_code = 400
    code = "error"

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.details = details
        super().__init__(message)


class ValidationAPIException(APIException):
    status_code = 400
    code = "validation_error"


class PermissionAPIException(APIException):
    status_code = 403
    code = "permission_denied"


class NotFoundAPIException(APIException):
    status_code = 404
    code = "not_found"


class ConflictAPIException(APIException):
    status_code = 409
    code = "conflict"