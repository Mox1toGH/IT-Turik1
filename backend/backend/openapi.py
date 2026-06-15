from drf_spectacular.utils import OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

# ---------------------------------------------------------------------------
# Reusable error response helpers
#
# All error bodies follow the shape produced by custom_exception_handler:
#   {
#     "code":    "<string>",   # e.g. "validation_error", "not_found", …
#     "message": "<string>",   # human-readable summary
#     "details": <object|null> # field-level errors for 400, null otherwise
#   }
# ---------------------------------------------------------------------------

def _error_response(description: str, code_example: str, with_details: bool = False) -> OpenApiResponse:
    fields: dict = {
        'code': drf_serializers.CharField(help_text='Machine-readable error code.'),
        'message': drf_serializers.CharField(help_text='Human-readable error summary.'),
        'details': (
            drf_serializers.DictField(
                child=drf_serializers.ListField(child=drf_serializers.CharField()),
                help_text='Field-level validation errors. Keys are field names, values are lists of messages.',
            )
            if with_details
            else drf_serializers.CharField(
                allow_null=True,
                default=None,
                help_text='Always null for non-validation errors.',
            )
        ),
    }
    return OpenApiResponse(
        response=inline_serializer(name=f'ErrorResponse_{code_example}', fields=fields),
        description=description,
    )


# Common reusable responses
_400 = _error_response(
    description='Validation error. `details` contains per-field error lists.',
    code_example='validation_error',
    with_details=True,
)
_401 = _error_response(
    description='Authentication credentials were not provided or are invalid.',
    code_example='not_authenticated',
)
_403 = _error_response(
    description='You do not have permission to perform this action.',
    code_example='permission_denied',
)
_404 = _error_response(
    description='Requested resource was not found.',
    code_example='not_found',
)
_503 = _error_response(
    description='Service temporarily unavailable.',
    code_example='service_unavailable',
)
