"""
Inventario técnico de endpoints y matriz RBAC de EFT (Etapa 7).

Este documento centraliza:
1) Endpoints expuestos por router.
2) Resource/action RBAC aplicados.
3) Restricciones adicionales por acción.
4) Observaciones de alcance por queryset/object permission.

Convenciones:
- role_scope: "ROLE:SCOPE" (ej. ADMIN_GENERAL:COMPANY)
- guards: permisos adicionales a RoleScopePermission.
- scoped_queryset: si get_queryset aplica scope_queryset(...).
"""

from apiUsuarios.rbac_contracts import Actions, Resources, Roles, Scopes


ROLE_SCOPE = {
    "SUPER_ADMIN_GLOBAL": f"{Roles.SUPER_ADMIN}:{Scopes.GLOBAL}",
    "ADMIN_GENERAL_COMPANY": f"{Roles.ADMIN_GENERAL}:{Scopes.COMPANY}",
    "AUDITOR_COMPANY": f"{Roles.AUDITOR}:{Scopes.COMPANY}",
    "CONTABILIDAD_COMPANY": f"{Roles.CONTABILIDAD}:{Scopes.COMPANY}",
    "RRHH_COMPANY": f"{Roles.RRHH}:{Scopes.COMPANY}",
    "LOGISTICA_COMPANY": f"{Roles.LOGISTICA}:{Scopes.COMPANY}",
    "COMERCIAL_COMPANY": f"{Roles.COMERCIAL}:{Scopes.COMPANY}",
    "INVENTARIO_COMPANY": f"{Roles.INVENTARIO}:{Scopes.COMPANY}",
    "EXTERNO_OWN": f"{Roles.USUARIO_EXTERNO}:{Scopes.OWN}",
}


ENDPOINT_PERMISSION_MATRIX = [
    {
        "module": "apiUsuarios",
        "base_path": "/api/usuarios/",
        "viewset": "UsuarioViewSet",
        "resource": Resources.USER,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create",
                "methods": ["POST"],
                "rbac_action": Actions.CREATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "update/partial_update",
                "methods": ["PUT", "PATCH"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission", "IsPropietarioOAdministrador"],
            },
            {
                "action": "destroy",
                "methods": ["DELETE"],
                "rbac_action": Actions.DELETE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "me",
                "methods": ["GET"],
                "rbac_action": "N/A (self endpoint)",
                "role_scope": ["Any authenticated user"],
                "guards": ["IsAuthenticated"],
            },
        ],
    },
    {
        "module": "apiUsuarios",
        "base_path": "/api/clientes/",
        "viewset": "ClienteViewSet",
        "resource": Resources.USER,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiUsuarios",
        "base_path": "/api/socios/",
        "viewset": "SocioViewSet",
        "resource": Resources.USER,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy/ajustar_saldo",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiUsuarios",
        "base_path": "/api/empleados/",
        "viewset": "EmpleadoViewSet",
        "resource": Resources.USER,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiUbicaciones",
        "base_path": "/api/{paises|departamentos|ciudades|ubicaciones|clientes-ubicaciones|socios-ubicaciones|empleados-ubicaciones}/",
        "viewset": "_BaseUbicacionViewSet + derivados",
        "resource": Resources.PEDIDO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiInventario",
        "base_path": "/api/productos/",
        "viewset": "ProductoViewSet",
        "resource": Resources.INVENTARIO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/bajo_stock/valor_total_inventario",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                    f"{Roles.USUARIO_EXTERNO}:{Scopes.COMPANY}",
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy/ajustar_stock",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiInventario",
        "base_path": "/api/movimientos-inventario/",
        "viewset": "MovimientoInventarioViewSet",
        "resource": Resources.INVENTARIO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/por_producto",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                    f"{Roles.USUARIO_EXTERNO}:{Scopes.COMPANY}",
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create",
                "methods": ["POST"],
                "rbac_action": Actions.CREATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiInventario",
        "base_path": "/api/{categorias-activo|activos-fijos|depreciaciones-activo|mantenimientos-activo|movimientos-activo}/",
        "viewset": "Activos ViewSets",
        "resource": Resources.INVENTARIO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve + custom GET (resumen_activos, alertas)",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                    f"{Roles.USUARIO_EXTERNO}:{Scopes.COMPANY}",
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy + calcular_mes",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["INVENTARIO_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiPedidos",
        "base_path": "/api/pedidos/",
        "viewset": "PedidoViewSet",
        "resource": Resources.PEDIDO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/mis_pedidos",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create",
                "methods": ["POST"],
                "rbac_action": Actions.CREATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "cambiar_estado/registrar_pago/asignar_interno",
                "methods": ["POST (action)"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["LOGISTICA_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
            {
                "action": "aprobar",
                "methods": ["POST (action)"],
                "rbac_action": Actions.APPROVE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministrador"],
            },
        ],
    },
    {
        "module": "apiImpuestos",
        "base_path": "/api/{impuestos|reglas-impuesto|asignaciones-impuesto|snapshots-impuesto|conceptos-laborales-empleado}/",
        "viewset": "Impuestos ViewSets",
        "resource": Resources.IMPUESTO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiBancos",
        "base_path": "/api/bancos/",
        "viewset": "BancoViewSet",
        "resource": Resources.BANCO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiCuentas",
        "base_path": "/api/cuentas/",
        "viewset": "CuentaViewSet",
        "resource": Resources.CUENTA,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiTransacciones",
        "base_path": "/api/transacciones/",
        "viewset": "TransaccionViewSet",
        "resource": Resources.TRANSACCION,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy/transferir",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno", "TransferenciaSerializer scope check"],
            },
        ],
    },
    {
        "module": "apiTransacciones",
        "base_path": "/api/categorias/",
        "viewset": "CategoriaViewSet",
        "resource": Resources.TRANSACCION,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "CRUD",
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "READ/CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            }
        ],
    },
    {
        "module": "apiTransacciones",
        "base_path": "/api/programaciones/",
        "viewset": "ProgramacionTransaccionViewSet",
        "resource": Resources.TRANSACCION,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/pendientes/activas/presupuesto_consolidado",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy/activar/desactivar/cancelar/ejecutar",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": Actions.UPDATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiTransacciones",
        "base_path": "/api/nominas/",
        "viewset": "NominaViewSet",
        "resource": Resources.TRANSACCION,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/pendientes/retrasadas/resumen_mensual",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
            {
                "action": "create/update/partial_update/destroy/aprobar_pago",
                "methods": ["POST", "PUT", "PATCH", "DELETE", "POST (action)"],
                "rbac_action": "CREATE/UPDATE/DELETE/APPROVE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministrador"],
            },
        ],
    },
    {
        "module": "apiDocumentos",
        "base_path": "/api/tipos-documento/",
        "viewset": "TipoDocumentoViewSet",
        "resource": Resources.DOCUMENTO,
        "scoped_queryset": "Activos visibles (activo=True); mutación restringida",
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create/update/partial_update/destroy",
                "methods": ["POST", "PUT", "PATCH", "DELETE"],
                "rbac_action": "CREATE/UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiDocumentos",
        "base_path": "/api/documentos/",
        "viewset": "DocumentoViewSet",
        "resource": Resources.DOCUMENTO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve/versiones/visualizar/descargar",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "create",
                "methods": ["POST"],
                "rbac_action": Actions.CREATE,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            },
            {
                "action": "update/partial_update/destroy",
                "methods": ["PUT", "PATCH", "DELETE"],
                "rbac_action": "UPDATE/DELETE",
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission", "IsAdministradorOrInterno"],
            },
        ],
    },
    {
        "module": "apiDocumentos",
        "base_path": "/api/accesos-documento/",
        "viewset": "AccesoDocumentoViewSet",
        "resource": Resources.DOCUMENTO,
        "scoped_queryset": True,
        "endpoints": [
            {
                "action": "list/retrieve",
                "methods": ["GET"],
                "rbac_action": Actions.READ,
                "role_scope": [
                    ROLE_SCOPE["SUPER_ADMIN_GLOBAL"],
                    ROLE_SCOPE["ADMIN_GENERAL_COMPANY"],
                    ROLE_SCOPE["CONTABILIDAD_COMPANY"],
                    ROLE_SCOPE["RRHH_COMPANY"],
                    ROLE_SCOPE["COMERCIAL_COMPANY"],
                    ROLE_SCOPE["AUDITOR_COMPANY"],
                    ROLE_SCOPE["EXTERNO_OWN"],
                ],
                "guards": ["RoleScopePermission"],
            }
        ],
    },
]

