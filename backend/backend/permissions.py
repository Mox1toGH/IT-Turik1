from enum import Enum

class Permission(Enum):
    CREATE_TOURNAMENT = 'create_tournament'
    EDIT_TOURNAMENT = 'edit_tournament'
    DELETE_TOURNAMENT = 'delete_tournament'
    VIEW_TOURNAMENT = 'view_tournament'
    MANAGE_PARTICIPANTS = 'manage_participants'
    MANAGE_ROUNDS = 'manage_rounds'
    MANAGE_ASSIGNMENTS = 'manage_assignments'
    MANAGE_EVALUATIONS = 'manage_evaluations'
    CREATE_NEWS = 'create_news'
    EDIT_NEWS = 'edit_news'
    DELETE_NEWS = 'delete_news'

ROLE_PERMISSIONS = {
    'admin': {
        # tournaments
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
    },

    'organizer': {
        # tournaments
        Permission.CREATE_TOURNAMENT,
        Permission.EDIT_TOURNAMENT,
        Permission.DELETE_TOURNAMENT,
        Permission.VIEW_TOURNAMENT,

        Permission.MANAGE_PARTICIPANTS,
        Permission.MANAGE_ROUNDS,

        # assignments only
        Permission.MANAGE_ASSIGNMENTS,

        # news
        Permission.CREATE_NEWS,
        Permission.EDIT_NEWS,
        Permission.DELETE_NEWS,
    },

    'jury': {
        Permission.VIEW_TOURNAMENT,
        Permission.MANAGE_EVALUATIONS,
    },
}


def has_permission(user, permission: Permission) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return permission in ROLE_PERMISSIONS.get(user.role, set())

def is_platform_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))
