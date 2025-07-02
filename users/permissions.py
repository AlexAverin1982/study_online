from rest_framework import permissions


# import logging


# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.debug("*"*100)

class IsModerator(permissions.BasePermission):
    def __init__(self):
        super(IsModerator, self).__init__()

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


class IsOwnProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj
