from rest_framework import permissions


class IsModerator(permissions.BasePermission):

    def has_object_pemission(self, request, view):
        return request.user.groups.filter(name='Moderators').exists()


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSuperUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
