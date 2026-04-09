from __future__ import annotations

from collections import defaultdict

from django.contrib.auth.models import Group
from rest_framework import permissions

from .rbac_contracts import Actions, Capability, Resources, Roles, Scopes


RESOURCE_GRANTS = {
    Resources.USER: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
        (Roles.USUARIO_EXTERNO, Actions.READ, Scopes.OWN),
        (Roles.USUARIO_EXTERNO, Actions.UPDATE, Scopes.OWN),
    ],
    Resources.PEDIDO: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.APPROVE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.ASSIGN, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.APPROVE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.ASSIGN, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.READ, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.CREATE, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.UPDATE, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.ASSIGN, Scopes.COMPANY),
        (Roles.COMERCIAL, Actions.READ, Scopes.COMPANY),
        (Roles.COMERCIAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.COMERCIAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
        (Roles.USUARIO_EXTERNO, Actions.READ, Scopes.OWN),
        (Roles.USUARIO_EXTERNO, Actions.CREATE, Scopes.OWN),
    ],
    Resources.INVENTARIO: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.READ, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.CREATE, Scopes.COMPANY),
        (Roles.LOGISTICA, Actions.UPDATE, Scopes.COMPANY),
        (Roles.INVENTARIO, Actions.READ, Scopes.COMPANY),
        (Roles.INVENTARIO, Actions.CREATE, Scopes.COMPANY),
        (Roles.INVENTARIO, Actions.UPDATE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
        (Roles.USUARIO_EXTERNO, Actions.READ, Scopes.COMPANY),
    ],
    Resources.IMPUESTO: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.READ, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.CREATE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.UPDATE, Scopes.COMPANY),
        (Roles.RRHH, Actions.READ, Scopes.COMPANY),
        (Roles.RRHH, Actions.CREATE, Scopes.COMPANY),
        (Roles.RRHH, Actions.UPDATE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
    ],
    Resources.BANCO: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.READ, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.CREATE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.UPDATE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
    ],
    Resources.CUENTA: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.READ, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.CREATE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.UPDATE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
    ],
    Resources.TRANSACCION: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.CREATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.UPDATE, Scopes.GLOBAL),
        (Roles.SUPER_ADMIN, Actions.DELETE, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.CREATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.UPDATE, Scopes.COMPANY),
        (Roles.ADMIN_GENERAL, Actions.DELETE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.READ, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.CREATE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.UPDATE, Scopes.COMPANY),
        (Roles.CONTABILIDAD, Actions.DELETE, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
    ],
    Resources.AUDITORIA: [
        (Roles.SUPER_ADMIN, Actions.READ, Scopes.GLOBAL),
        (Roles.ADMIN_GENERAL, Actions.READ, Scopes.COMPANY),
        (Roles.AUDITOR, Actions.READ, Scopes.COMPANY),
    ],
}

SCOPE_ORDER = {
    Scopes.OWN: 1,
    Scopes.TEAM: 2,
    Scopes.DEPARTMENT: 3,
    Scopes.COMPANY: 4,
    Scopes.GLOBAL: 5,
}

OWNER_FIELDS = ("usuario", "cliente", "empleado", "owner", "user", "interno_asignado")

METHOD_ACTION_MAP = {
    "GET": Actions.READ,
    "POST": Actions.CREATE,
    "PUT": Actions.UPDATE,
    "PATCH": Actions.UPDATE,
    "DELETE": Actions.DELETE,
}


def _max_scope(scopes: list[str]) -> str | None:
    if not scopes:
        return None
    return max(scopes, key=lambda scope: SCOPE_ORDER.get(scope, 0))


def get_user_roles(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    roles = set()
    if user.is_superuser:
        roles.add(Roles.SUPER_ADMIN)

    if hasattr(user, "empleado"):
        roles.add(Roles.ADMIN_GENERAL)
    elif hasattr(user, "socio"):
        roles.add(Roles.USUARIO_EXTERNO)
    elif hasattr(user, "cliente"):
        roles.add(Roles.USUARIO_EXTERNO)

    group_names = set(Group.objects.filter(user=user).values_list("name", flat=True))
    valid_group_roles = {
        Roles.SUPER_ADMIN,
        Roles.ADMIN_GENERAL,
        Roles.AUDITOR,
        Roles.CONTABILIDAD,
        Roles.RRHH,
        Roles.LOGISTICA,
        Roles.COMERCIAL,
        Roles.INVENTARIO,
        Roles.SOPORTE,
        Roles.USUARIO_EXTERNO,
    }
    roles |= group_names.intersection(valid_group_roles)
    return roles


def get_capability_scope(user, resource: str, action: str) -> str | None:
    roles = get_user_roles(user)
    scopes = []
    for role, grant_action, grant_scope in RESOURCE_GRANTS.get(resource, []):
        if role in roles and grant_action == action:
            scopes.append(grant_scope)
    return _max_scope(scopes)


def build_capabilities(user) -> list[dict]:
    roles = get_user_roles(user)
    capabilities = []
    for resource, grants in RESOURCE_GRANTS.items():
        action_to_scope = defaultdict(list)
        for role, action, scope in grants:
            if role in roles:
                action_to_scope[action].append(scope)
        for action, scopes in action_to_scope.items():
            capability_scope = _max_scope(scopes)
            if capability_scope:
                capabilities.append(Capability(resource, action, capability_scope).__dict__)
    return sorted(capabilities, key=lambda c: (c["resource"], c["action"]))


def _resolve_owner_filter(model, user):
    model_field_names = {f.name for f in model._meta.get_fields() if hasattr(f, "name")}
    for owner_field in OWNER_FIELDS:
        if owner_field in model_field_names:
            return {owner_field: user}
    if hasattr(user, "_meta") and model == user._meta.model:
        return {"id": user.id}
    return None


def scope_queryset(queryset, user, scope: str):
    if scope in (Scopes.GLOBAL, Scopes.COMPANY):
        return queryset
    owner_filter = _resolve_owner_filter(queryset.model, user)
    if owner_filter:
        return queryset.filter(**owner_filter)
    return queryset.none()


def has_object_scope(user, obj, scope: str) -> bool:
    if scope in (Scopes.GLOBAL, Scopes.COMPANY):
        return True
    if hasattr(obj, "id") and hasattr(user, "_meta") and obj.__class__ == user._meta.model:
        return obj.id == user.id
    for owner_field in OWNER_FIELDS:
        if hasattr(obj, owner_field):
            return getattr(obj, owner_field) == user
    return False


class RoleScopePermission(permissions.BasePermission):
    message = "No cuenta con permisos suficientes para esta acción."

    def _resolve_action(self, request, view):
        action_map = getattr(view, "rbac_action_map", {})
        if view.action in action_map:
            return action_map[view.action]
        return METHOD_ACTION_MAP.get(request.method, Actions.READ)

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        resource = getattr(view, "rbac_resource", None)
        if not resource:
            return False
        action = self._resolve_action(request, view)
        scope = get_capability_scope(request.user, resource, action)
        if not scope:
            return False
        request._eft_scope = scope
        return True

    def has_object_permission(self, request, view, obj):
        scope = getattr(request, "_eft_scope", None)
        if not scope:
            return False
        return has_object_scope(request.user, obj, scope)


class IsAdministradorOrInterno(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_administrador() or request.user.es_interno() or hasattr(request.user, "empleado")


class IsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.es_administrador()


class IsPropietarioOAdministrador(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.es_administrador():
            return True
        if hasattr(obj, "usuario"):
            return obj.usuario == request.user
        if isinstance(obj, type(request.user)):
            return obj == request.user
        return False


class EsClienteOSuperior(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class EsSocioOSuperior(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.es_socio()
            or request.user.es_interno()
            or request.user.es_administrador()
            or hasattr(request.user, "empleado")
        )
