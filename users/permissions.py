from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем (включая гостей).
    Изменение/удаление только владельцу профиля.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user