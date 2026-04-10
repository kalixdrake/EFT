"""
Contratos base de RBAC para EFT v1 (Etapa 0).

Este módulo define vocabulario común para las etapas siguientes sin
forzar todavía cambios de base de datos ni de comportamiento operativo.
"""

from __future__ import annotations

from dataclasses import dataclass


class Roles:
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN_GENERAL = "ADMIN_GENERAL"
    AUDITOR = "AUDITOR"
    CONTABILIDAD = "CONTABILIDAD"
    RRHH = "RRHH"
    LOGISTICA = "LOGISTICA"
    COMERCIAL = "COMERCIAL"
    INVENTARIO = "INVENTARIO"
    SOPORTE = "SOPORTE"
    USUARIO_EXTERNO = "USUARIO_EXTERNO"


class Scopes:
    OWN = "OWN"
    TEAM = "TEAM"
    DEPARTMENT = "DEPARTMENT"
    COMPANY = "COMPANY"
    GLOBAL = "GLOBAL"


class Actions:
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    ASSIGN = "assign"


class Resources:
    USER = "user"
    PEDIDO = "pedido"
    INVENTARIO = "inventario"
    IMPUESTO = "impuesto"
    TRANSACCION = "transaccion"
    DOCUMENTO = "documento"
    BANCO = "banco"
    CUENTA = "cuenta"
    AUDITORIA = "auditoria"


@dataclass(frozen=True)
class Capability:
    resource: str
    action: str
    scope: str


FRONTEND_MENU_CATALOG = [
    {
        "id": "dashboard",
        "label": "Dashboard",
        "route": "/dashboard",
        "icon": "layout-dashboard",
        "resource": Resources.USER,
        "actions": [Actions.READ],
        "order": 10,
    },
    {
        "id": "usuarios",
        "label": "Usuarios",
        "route": "/usuarios",
        "icon": "users",
        "resource": Resources.USER,
        "actions": [Actions.READ],
        "order": 20,
    },
    {
        "id": "pedidos",
        "label": "Pedidos",
        "route": "/pedidos",
        "icon": "shopping-cart",
        "resource": Resources.PEDIDO,
        "actions": [Actions.READ],
        "order": 30,
    },
    {
        "id": "inventario",
        "label": "Inventario",
        "route": "/inventario",
        "icon": "package",
        "resource": Resources.INVENTARIO,
        "actions": [Actions.READ],
        "order": 40,
    },
    {
        "id": "impuestos",
        "label": "Impuestos y Nomina",
        "route": "/impuestos",
        "icon": "calculator",
        "resource": Resources.IMPUESTO,
        "actions": [Actions.READ],
        "order": 50,
    },
    {
        "id": "documentos",
        "label": "Documentos",
        "route": "/documentos",
        "icon": "file-text",
        "resource": Resources.DOCUMENTO,
        "actions": [Actions.READ],
        "order": 60,
    },
    {
        "id": "finanzas",
        "label": "Finanzas",
        "route": "/finanzas",
        "icon": "landmark",
        "resource": Resources.TRANSACCION,
        "actions": [Actions.READ],
        "order": 70,
    },
    {
        "id": "auditoria",
        "label": "Auditoria",
        "route": "/auditoria",
        "icon": "shield-check",
        "resource": Resources.AUDITORIA,
        "actions": [Actions.READ],
        "order": 80,
    },
]
