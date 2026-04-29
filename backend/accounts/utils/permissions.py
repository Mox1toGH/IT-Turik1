class Permission:
    CREATE_TOURNAMENT = 'create_tournament'


ROLE_PERMISSIONS = {
    'admin': {
        Permission.CREATE_TOURNAMENT,
    },
    'organizer': {
        Permission.CREATE_TOURNAMENT,
    },
    'team': set(),
    'jury': set(),
}


def is_platform_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == 'admin'))


def has_permission(user, permission):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return permission in ROLE_PERMISSIONS.get(user.role, set())
