from enum import Enum
from backend.errors import raise_api_error
from http import HTTPStatus

class Permission(Enum):
    MANAGE_ROLE_CODES = 'manage_role_codes'
    CREATE_TOURNAMENT = 'create_tournament'
    EDIT_TOURNAMENT = 'edit_tournament'
    DELETE_TOURNAMENT = 'delete_tournament'
    VIEW_TOURNAMENT = 'view_tournament'
    
    MANAGE_PARTICIPANTS = 'manage_participants'
    MANAGE_ROUNDS = 'manage_rounds'
    MANAGE_EVENTS = 'manage_events'
    MANAGE_ASSIGNMENTS = 'manage_assignments'
    MANAGE_EVALUATIONS = 'manage_evaluations'
    
    CREATE_TEAM = 'create_team'
    CREATE_NEWS = 'create_news'
    EDIT_NEWS = 'edit_news'
    DELETE_NEWS = 'delete_news'

    MANAGE_CERTIFICATES = 'create_certificates'
    MANAGE_CERTIFICATE_TEMPLATES = 'manage_certificate_templates'
    
ROLE_PERMISSIONS = {
    'admin': {
        # tournaments
        Permission.MANAGE_ROLE_CODES,
        Permission.CREATE_TOURNAMENT,
        Permission.EDIT_TOURNAMENT,
        Permission.DELETE_TOURNAMENT,
        Permission.VIEW_TOURNAMENT,

        Permission.MANAGE_PARTICIPANTS,
        Permission.MANAGE_ROUNDS,

        # jury
        Permission.MANAGE_ASSIGNMENTS,
        Permission.MANAGE_EVALUATIONS,

        # news
        Permission.CREATE_NEWS,
        Permission.EDIT_NEWS,
        Permission.DELETE_NEWS,

        # certificates
        Permission.MANAGE_CERTIFICATES,
        Permission.MANAGE_CERTIFICATE_TEMPLATES
    },

    'organizer': {
        # tournaments
        Permission.CREATE_TOURNAMENT,
        Permission.EDIT_TOURNAMENT,
        Permission.DELETE_TOURNAMENT,
        Permission.VIEW_TOURNAMENT,

        Permission.MANAGE_PARTICIPANTS,
        Permission.MANAGE_ROUNDS,
        Permission.MANAGE_EVENTS,

        # assignments only
        Permission.MANAGE_ASSIGNMENTS,

        # news
        Permission.CREATE_NEWS,
        Permission.EDIT_NEWS,
        Permission.DELETE_NEWS,

        # certificates
        Permission.MANAGE_CERTIFICATES,
        Permission.MANAGE_CERTIFICATE_TEMPLATES
    },

    'jury': {
        Permission.VIEW_TOURNAMENT,
        Permission.MANAGE_EVALUATIONS,
    },
}

def require_permission(request, permission: Permission):
    if not has_permission(request.auth, permission):
        raise_api_error(HTTPStatus.FORBIDDEN, 'You do not have permission to perform this action.')


def has_permission(user, permission: Permission) -> bool:
    if not user or not user.is_authenticated:
        return False

    return permission in ROLE_PERMISSIONS.get(user.role, set())
    

def is_platform_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))
