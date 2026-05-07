from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    normalized_data = _normalize_data(response.data)
    status_code = response.status_code
    code = _code_for_status(status_code)
    message = _extract_message(normalized_data, status_code)
    details = None

    if status_code == status.HTTP_400_BAD_REQUEST:
        details = _extract_validation_details(normalized_data)

    response.data = {
        "code": code,
        "message": message,
        "details": details,
    }

    return response


def _extract_validation_details(normalized_data):
    if isinstance(normalized_data, dict):
        details = {
            key: value
            for key, value in normalized_data.items()
            if key not in {'detail', 'message', 'status', 'error', 'message'}
        }
        return details or None

    return None


def _normalize_data(data):
    if isinstance(data, dict):
        return {key: _normalize_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_normalize_data(item) for item in data]
    return str(data)


def _extract_message(normalized_data, status_code):
    if isinstance(normalized_data, dict):
        reserved_keys = {'detail', 'message', 'status', 'error'}
        validation_fields = {k: v for k, v in normalized_data.items() if k not in reserved_keys}
        
        # For validation errors (400), build a comprehensive message from field errors
        if status_code == status.HTTP_400_BAD_REQUEST:
            validation_message = _format_validation_message(normalized_data)
            if validation_message:
                return validation_message
        
        # Fallback chain: message -> detail -> fields -> default -> Unknown error
        message = (
            _extract_first_string(normalized_data.get('message'))
            or _extract_first_string(normalized_data.get('detail'))
            or _extract_first_string(validation_fields)
            or _default_message_for_status(status_code)
        )
        return message or 'Unknown error'
    
    if isinstance(normalized_data, list):
        return _extract_first_string(normalized_data) or _default_message_for_status(status_code) or 'Unknown error'
    
    if isinstance(normalized_data, str):
        return normalized_data or 'Unknown error'
    
    return _default_message_for_status(status_code) or 'Unknown error'


def _format_validation_message(data):
    """
    Build a comprehensive validation error message from field errors.
    Example: "team: This field is required. email: Invalid email format."
    """
    error_messages = []
    excluded_keys = {'detail', 'message', 'status', 'error'}
    
    for key, value in data.items():
        if key in excluded_keys:
            continue
        
        # Extract error message for this field
        field_error = _extract_first_string(value)
        if field_error:
            error_messages.append(f"{key}: {field_error}")
    
    # Join all error messages with ". " separator
    if error_messages:
        return ". ".join(error_messages) + "."
    
    return None


def _extract_first_string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for item in value:
            nested = _extract_first_string(item)
            if nested:
                return nested
        return None
    if isinstance(value, dict):
        for item in value.values():
            nested = _extract_first_string(item)
            if nested:
                return nested
    return None


def _code_for_status(status_code):
    mapping = {
        status.HTTP_400_BAD_REQUEST: 'validation_error',
        status.HTTP_401_UNAUTHORIZED: 'not_authenticated',
        status.HTTP_403_FORBIDDEN: 'permission_denied',
        status.HTTP_404_NOT_FOUND: 'not_found',
        status.HTTP_429_TOO_MANY_REQUESTS: 'too_many_requests',
        status.HTTP_500_INTERNAL_SERVER_ERROR: 'server_error',
    }
    return mapping.get(status_code, 'error')


def _default_message_for_status(status_code):
    defaults = {
        status.HTTP_400_BAD_REQUEST: 'Invalid input data.',
        status.HTTP_401_UNAUTHORIZED: 'Authentication required.',
        status.HTTP_403_FORBIDDEN: 'Permission denied.',
        status.HTTP_404_NOT_FOUND: 'Resource not found.',
        status.HTTP_429_TOO_MANY_REQUESTS: 'Too many requests.',
        status.HTTP_500_INTERNAL_SERVER_ERROR: 'Server error.',
    }
    return defaults.get(status_code, 'Request failed.')