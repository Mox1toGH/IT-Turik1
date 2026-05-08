from rest_framework.permissions import BasePermission, SAFE_METHODS

from backend.permissions import is_platform_admin


class IsNotPlatformAdmin(BasePermission):
    message = 'Platform admins cannot manage teams.'

    def has_permission(self, request, view):
        return not is_platform_admin(request.user)


class IsNotPlatformAdminOrReadOnly(IsNotPlatformAdmin):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class CanCreateTeam(IsNotPlatformAdmin):
    pass


class CanMutateTeam(IsNotPlatformAdmin):
    pass
