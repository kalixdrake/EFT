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
