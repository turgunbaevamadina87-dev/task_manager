from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу задачи
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user