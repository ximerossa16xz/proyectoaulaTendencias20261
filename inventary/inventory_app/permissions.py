from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        # GET permitido para todos los autenticados
        if request.method in SAFE_METHODS:
            return True

        # POST, PUT, DELETE → solo admin
        return request.user.role == 'admin'