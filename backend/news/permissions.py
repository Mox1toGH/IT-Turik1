from rest_framework.permissions import SAFE_METHODS, BasePermission

from backend.permissions import Permission, has_permission as user_has_permission


class HasNewsPermission(BasePermission):
    message = 'News permission required.'
    required_permission = None

    def has_permission(self, request, view):
        return user_has_permission(request.user, self.required_permission)


class HasNewsPermissionOrReadOnly(HasNewsPermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class CanCreateNews(HasNewsPermission):
    required_permission = Permission.CREATE_NEWS


class CanEditNews(HasNewsPermission):
    required_permission = Permission.EDIT_NEWS

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'organizer':
            return obj.created_by_id == request.user.id
        return False


class CanDeleteNews(HasNewsPermission):
    required_permission = Permission.DELETE_NEWS

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'organizer':
            return obj.created_by_id == request.user.id
        return False


class CanManageNewsOrReadOnly(HasNewsPermissionOrReadOnly):
    required_permission = Permission.CREATE_NEWS
