from rest_framework import permissions


class IsModerator(permissions.BasePermission):

    def has_pemission(self, request, view):
        return not (request.user.groups.filter(name='Moderators').exists())


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
