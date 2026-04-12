
Migración estructurada hacia un monorepo real (`/backend`, `/frontend`), con validaciones continuas. Contempla la estabilización del backend, una reimplementación completa y limpia de la IA acoplada al esquema actual de permisos usando `apiInteracciones`, y el inicio de Flutter Web (preparado para escalabilidad móvil).

**Pasos**

**Fase 1: Migración a Monorepo y Aislamiento Backend**
1. Crear el directorio `backend/` en la raíz del proyecto.
2. Mover componentes de Django a `backend/`: `api*`, `EFT/`, `manage.py`, `requirements.txt`, `db.sqlite3`, `media/`, `staticfiles/`, `integrations/`, `json/`, `llms/`, `dockerfile`.
3. Actualizar rutas en scripts de utilidad como `docker-utils.sh` *(depende de paso 2)*.
4. Modificar `docker-compose.yml` y `docker-compose.prod.yml`: ajustar el `build.context` de `web` hacia `./backend`, y los volúmenes de base de datos/archivos mapeando a las nuevas rutas.
5. Actualizar la configuración de Nginx (`nginx/`) para apuntar correctamente estáticos y media a las rutas relativas nuevas.

**Fase 2: Refactorización e Integración de IA en `apiInteracciones`**
1. Utilizar y expandir la app existente `apiInteracciones` dentro de `backend/` como núcleo del chat y trazabilidad.
2. Reescribir por completo la lógica de integración con la IA (actualmente en `integrations/ai.py` y `integrations/ai_prompts.py`) para que sea más limpia y modular.
3. Desarrollar endpoint `POST /api/interacciones/chat/` que reciba el prompt.
4. Integrar RBAC directamente en la generación de prompts: El endpoint debe verificar el rol y las `capabilities` del usuario en sesión (Etapa 10) para inyectar un *system prompt* personalizado que delimite exactamente qué modulo/datos financieros puede consultar.

**Fase 3: Bootstrap de Flutter Web (Preparación Móvil)**
1. Inicializar el proyecto Flutter en root: `flutter create --platforms web,android,ios frontend/` *(paralelo a fase 2)*.
2. Ajustar backend para permitir CORS desde Flutter Web.
3. Instalar dependencias base en Flutter: `dio`, `riverpod`/`provider`, y `go_router`.
4. Implementar invocador y validador de Sesión: consumo inicial de `/api/usuarios/me/`, `/api/usuarios/capacidades/`, `/api/usuarios/menu/`.
5. Crear el utility de autorización global en Flutter `can(resource, action)`.
6. Configurar el `go_router` con guards basados en sesión.

**Fase 4: Actualización de Documentación**
1. Modificar y versionar documentación técnica añadiendo la capa monorepo y la especificación de diseño IA-RBAC.

**Archivos Relevantes**
- [docker-compose.yml](docker-compose.yml) — Contextos y volúmenes a cambiar.
- [apiInteracciones/views/](apiInteracciones/views/) (hacia futura `backend/apiInteracciones`) — Nuevo endpoint de IA basado en contexto de usuario.
- `[frontend/lib/core/auth/auth_service.dart]` — Próximos contratos en Flutter de tus roles/policies.

**Verificación**
1. **Fase 1:** Contenedores subidos (`docker compose up`) y test pasando limpiamente desde su nueva raíz.
2. **Fase 2:** Unit Testing estricto de seguridad de la IA asumiendo identidades (cliente vs admin general); simular escenarios donde a ciertos clientes la IA se niega a resolver el prompt.
3. **Fase 3:** Confirmar que flutter levanta localmente el router usando la capa CORS liberada y logra un Bootstrap 200 logueando las capabilities en base de tu matriz.

**Decisiones**
- La inteligencia artificial heredará el árbol de decisiones del core de Seguridad; el prompt debe bloquear el acceso a recursos incluso si el RAG o la base de datos se equivocan.
- El repositorio cambia de "Solo Django" a una verdadera distribución Monorepo.

## Guía de integración frontend (flujo recomendado)

## Bootstrap de sesión

1. Login/auth en frontend.
2. Consumir `GET /api/usuarios/me/`.
3. Consumir `GET /api/usuarios/capacidades/`.
4. Consumir `GET /api/usuarios/menu/`.

Con estos tres endpoints, el frontend puede:

- Renderizar perfil e identidad (`tipo_entidad`).
- Encender/apagar acciones por `resource/action`.
- Construir menú visible y rutas habilitadas.

## Regla de autorización en frontend

Nunca hardcodear permisos por nombre de rol únicamente.

Usar `capabilities` como fuente de verdad:

- `can(resource, action)` => existe capability con ese par.
- `scope(resource, action)` => nivel de alcance (`OWN`, `COMPANY`, `GLOBAL`).

Ejemplo:

- Botón “Crear transacción” visible solo si `can("transaccion", "create")`.
- Botón “Eliminar cuenta” visible solo si `can("cuenta", "delete")`.

## Manejo de errores de autorización

El frontend debe manejar:

- `401`: sesión no válida/expirada.
- `403`: usuario autenticado sin permiso.
- `404` en recursos con scope estricto: tratar como “no accesible/no existe para el usuario”.

Recomendación UX:

- `403`: mensaje “No cuenta con permisos para esta acción”.
- `404` en detalle protegido: volver al listado sin exponer existencia del recurso.

## Estrategia para tablas/listados

Backend ya filtra por scope en `get_queryset`.

En frontend:

- No asumir que el usuario verá todos los registros.
- Evitar mostrar contadores globales no soportados por backend.
- Implementar paginación/filtros sin lógica de permisos en cliente.

## Custom actions sensibles

Acciones de alto riesgo deben depender de capabilities:

- Pedidos: `aprobar`, `cambiar_estado`, `asignar_interno`.
- Transacciones: `transferir`.
- Inventario: `ajustar_stock`.
- Documentos: `visualizar`, `descargar`, `versiones`.

El frontend debe:

- esconder CTA si no hay capability;
- igualmente manejar 403/404 por seguridad server-side.

---

## Inventario resumido de módulos para frontend

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

