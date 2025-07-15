from rest_framework import permissions


class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        # logger.debug("Checking permissions for user: %s", request.user)
        result = request.user.groups.filter(name='Moderators').exists()
        # logger.debug("Permission check result: %s", result)
        return result

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Moderators').exists():
            return True
        return False


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class IsAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj
