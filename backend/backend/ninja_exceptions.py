from ninja.errors import HttpError


def error_code_for_status(status_code):
    return {
        400: 'validation_error',
        401: 'not_authenticated',
        403: 'permission_denied',
        404: 'not_found',
        429: 'too_many_requests',
        503: 'service_unavailable',
        500: 'server_error',
    }.get(status_code, 'error')


def _first_message(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for field, message in value.items():
            return f'{field}: {_first_message(message)}'
    if isinstance(value, (list, tuple)) and value:
        return _first_message(value[0])
    return 'Invalid input data.'


class ValidationError(HttpError):
    """Ninja validation error with field-level details for API clients."""

    def __init__(self, details):
        self.details = details
        super().__init__(400, _first_message(details))
