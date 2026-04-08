from rest_framework import permissions


class IsAdministradorOrInterno(permissions.BasePermission):
    """
    Permiso personalizado: Solo permite acceso a usuarios con rol ADMINISTRADOR o INTERNO
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_administrador() or request.user.es_interno()


class IsAdministrador(permissions.BasePermission):
    """
    Permiso personalizado: Solo permite acceso a usuarios con rol ADMINISTRADOR
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_administrador()


class IsPropietarioOAdministrador(permissions.BasePermission):
    """
    Permiso personalizado: Permite acceso al propietario del recurso o a administradores
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores tienen acceso total
        if request.user.es_administrador():
            return True
        
        # El propietario tiene acceso a sus propios recursos
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        # Si el objeto es un Usuario, verificar que sea el mismo
        if isinstance(obj, type(request.user)):
            return obj == request.user
        
        return False


class EsClienteOSuperior(permissions.BasePermission):
    """
    Permite acceso a CLIENTE y roles superiores (SOCIO, INTERNO, ADMINISTRADOR)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True  # Cualquier usuario autenticado


class EsSocioOSuperior(permissions.BasePermission):
    """
    Permite acceso a SOCIO y roles superiores (INTERNO, ADMINISTRADOR)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ['SOCIO', 'INTERNO', 'ADMINISTRADOR']
