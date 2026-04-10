# Etapa 10 - QA de seguridad de permisos e integración frontend

## 1. Resultado de la etapa

En esta etapa se fortaleció la seguridad de permisos con foco en:

- Escalamiento vertical (roles intentando ejecutar acciones de mayor privilegio).
- Escalamiento lateral/horizontal (usuarios accediendo recursos de otros usuarios).
- Contrato operativo para frontend basado en `capabilities` y `menu`.

Además, se documenta el inventario de endpoints y la forma recomendada de integración para frontend.

---

## 2. Arquitectura de permisos vigente

### 2.1 Núcleo RBAC

- Módulo: `apiUsuarios/permissions.py`
- Componentes clave:
  - `RoleScopePermission`: resuelve permiso por `resource + action`.
  - `RESOURCE_GRANTS`: matriz rol/acción/alcance.
  - `scope_queryset(queryset, user, scope)`: aplica filtrado por alcance (`OWN`, `COMPANY`, `GLOBAL`).
  - `has_object_scope(user, obj, scope)`: control de acceso a objeto puntual.

### 2.2 Contrato para frontend

- `GET /api/usuarios/capacidades/`
  - Retorna:
    - `roles`
    - `capabilities[]` con `{resource, action, scope}`
- `GET /api/usuarios/menu/`
  - Retorna `items[]` del menú permitido por capacidades.

### 2.3 Mapa de endpoints y permisos

- Matriz de referencia: `EFT/endpoint_permission_matrix.py`
- Rutas globales: `EFT/urls.py`
- OpenAPI:
  - `GET /api/schema/`
  - `GET /api/docs/`

---

## 3. Hallazgos y ajuste aplicado

### 3.1 Hallazgo crítico corregido (P0)

**Problema:** cualquier usuario con entidad `empleado` recibía rol `ADMIN_GENERAL` de forma implícita.

- Ubicación corregida: `apiUsuarios/permissions.py`, función `get_user_roles`.
- Riesgo: escalamiento vertical (auditor/contabilidad/etc. con privilegios de admin).
- Corrección: se removió la asignación automática de `ADMIN_GENERAL` por `hasattr(user, "empleado")`.  
  Ahora `ADMIN_GENERAL` solo proviene de superusuario o grupo explícito.

---

## 4. Cobertura de pruebas Stage 10 agregada

### 4.1 Usuarios

Archivo: `apiUsuarios/tests/test_stage10_security.py`

- `test_auditor_empleado_no_puede_crear_usuario`
- `test_auditor_capacidades_no_incluyen_admin_general`

Cobertura:
- Bloquea escalamiento vertical de auditor a admin.
- Valida contrato `capabilities` consistente con RBAC real.

### 4.2 Pedidos

Archivo: `apiPedidos/tests_stage10_security.py`

- `test_cliente_a_no_puede_ver_detalle_pedido_cliente_b`
- `test_logistica_no_puede_aprobar_pedido`
- `test_cliente_no_puede_crear_pedido_para_otro_usuario`

Cobertura:
- Escalamiento lateral entre externos (404 por scope).
- Escalamiento vertical (LOGISTICA no aprueba).
- Bloqueo de creación lateral de pedido para tercero.

### 4.3 Transacciones/Nómina

Archivo: `apiTransacciones/tests/test_stage10_security.py`

- `test_auditor_no_puede_crear_transaccion`
- `test_auditor_no_puede_transferir`
- `test_usuario_externo_no_puede_crear_nomina`

Cobertura:
- Auditor en modo solo lectura.
- Externo sin permisos de mutación financiera/nomina.

### 4.4 Documentos

Archivo: `apiDocumentos/tests_stage10_security.py`

- `test_cliente_a_no_puede_ver_documento_cliente_b`
- `test_cliente_a_no_puede_descargar_documento_cliente_b`

Cobertura:
- Aislamiento horizontal por propietario.

### 4.5 Bancos

Archivo: `apiBancos/tests/test_stage10_security.py`

- `test_externo_no_puede_crear_banco`
- `test_contabilidad_no_puede_eliminar_banco`

Cobertura:
- Externo sin mutación.
- Contabilidad sin `delete` (solo hasta `update` por contrato).

### 4.6 Cuentas

Archivo: `apiCuentas/tests/test_stage10_security.py`

- `test_externo_no_puede_crear_cuenta`
- `test_auditor_no_puede_actualizar_cuenta`
- `test_contabilidad_no_puede_eliminar_cuenta`

Cobertura:
- Externo sin mutación.
- Auditor read-only.
- Contabilidad sin `delete`.

---

## 5. Cambio funcional aplicado en negocio de pedidos

Archivo: `apiPedidos/serializers/pedido_serializer.py`

Se añadió validación en `PedidoCreateSerializer.validate()`:

- Si el usuario no es admin, no puede crear pedidos con `cliente` distinto a sí mismo.
- Si no envía `cliente`, se autocompleta con su usuario.

Esto bloquea un vector de escalamiento lateral (crear pedidos en nombre de otro usuario externo).

---

## 6. Guía de integración frontend (flujo recomendado)

## 6.1 Bootstrap de sesión

1. Login/auth en frontend.
2. Consumir `GET /api/usuarios/me/`.
3. Consumir `GET /api/usuarios/capacidades/`.
4. Consumir `GET /api/usuarios/menu/`.

Con estos tres endpoints, el frontend puede:

- Renderizar perfil e identidad (`tipo_entidad`).
- Encender/apagar acciones por `resource/action`.
- Construir menú visible y rutas habilitadas.

## 6.2 Regla de autorización en frontend

Nunca hardcodear permisos por nombre de rol únicamente.

Usar `capabilities` como fuente de verdad:

- `can(resource, action)` => existe capability con ese par.
- `scope(resource, action)` => nivel de alcance (`OWN`, `COMPANY`, `GLOBAL`).

Ejemplo:

- Botón “Crear transacción” visible solo si `can("transaccion", "create")`.
- Botón “Eliminar cuenta” visible solo si `can("cuenta", "delete")`.

## 6.3 Manejo de errores de autorización

El frontend debe manejar:

- `401`: sesión no válida/expirada.
- `403`: usuario autenticado sin permiso.
- `404` en recursos con scope estricto: tratar como “no accesible/no existe para el usuario”.

Recomendación UX:

- `403`: mensaje “No cuenta con permisos para esta acción”.
- `404` en detalle protegido: volver al listado sin exponer existencia del recurso.

## 6.4 Estrategia para tablas/listados

Backend ya filtra por scope en `get_queryset`.

En frontend:

- No asumir que el usuario verá todos los registros.
- Evitar mostrar contadores globales no soportados por backend.
- Implementar paginación/filtros sin lógica de permisos en cliente.

## 6.5 Custom actions sensibles

Acciones de alto riesgo deben depender de capabilities:

- Pedidos: `aprobar`, `cambiar_estado`, `asignar_interno`.
- Transacciones: `transferir`.
- Inventario: `ajustar_stock`.
- Documentos: `visualizar`, `descargar`, `versiones`.

El frontend debe:

- esconder CTA si no hay capability;
- igualmente manejar 403/404 por seguridad server-side.

---

## 7. Inventario resumido de módulos para frontend

- Usuarios (`/api/usuarios`, `/api/clientes`, `/api/socios`, `/api/empleados`)
  - Contrato de sesión: `/api/usuarios/me/`, `/api/usuarios/capacidades/`, `/api/usuarios/menu/`
- Pedidos (`/api/pedidos`)
  - acciones: `aprobar`, `cambiar_estado`, `registrar_pago`, `asignar_interno`, `mis_pedidos`
- Inventario (`/api/productos`, `/api/movimientos-inventario`)
  - acciones: `bajo_stock`, `valor_total_inventario`, `ajustar_stock`, `por_producto`
- Finanzas (`/api/transacciones`, `/api/categorias`, `/api/programaciones`, `/api/nominas`)
  - acciones: `transferir`, `pendientes`, `activas`, `ejecutar`, `aprobar_pago`, etc.
- Documentos (`/api/documentos`, `/api/tipos-documento`, `/api/accesos-documento`)
  - acciones: `versiones`, `visualizar`, `descargar`
- Auditoría (`/api/auditoria-eventos`)
- Soporte de dominio: bancos, cuentas, ubicaciones, impuestos.

---

## 8. Comandos de prueba recomendados para etapa 10

- Suite completa (entorno con Git Bash):
  - `USE_SQLITE=true python manage.py test -v 1`

- Foco en seguridad stage 10:
  - `USE_SQLITE=true python manage.py test apiUsuarios.tests.test_stage10_security apiPedidos.tests_stage10_security apiTransacciones.tests.test_stage10_security apiDocumentos.tests_stage10_security apiBancos.tests.test_stage10_security apiCuentas.tests.test_stage10_security -v 1`

---

## 9. Qué hay, qué se puede hacer y cómo hacerlo (resumen operativo)

### Qué hay

- RBAC por recurso/acción/alcance.
- Contrato frontend de capacidades y menú.
- Endpoints de negocio por módulos con acciones custom.
- Auditoría transversal en endpoints críticos.

### Qué se puede hacer

- Construir UI y navegación dinámica por permisos reales.
- Aplicar guards de botones/rutas por capabilities.
- Consumir módulos funcionales de usuarios, pedidos, inventario, finanzas, documentos y auditoría.

### Cómo hacerlo

1. Inicializar sesión con `me + capacidades + menu`.
2. Mantener un helper central `can(resource, action)`.
3. Condicionar rutas y acciones por capabilities.
4. Manejar 401/403/404 de forma explícita.
5. No duplicar seguridad en cliente: backend es la autoridad final.

