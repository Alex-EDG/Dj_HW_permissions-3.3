from rest_framework import permissions


class IsOwnerOrAdminOnly(permissions.BasePermission):

    message = 'Действие разрешено только владельцам и администраторам'

    def has_object_permission(self, request, view, obj):
        # Разрешено только для методов GET, HEAD и OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить доступ только создателю объекта или superuser
        return obj.creator == request.user or (request.user and request.user.is_staff)