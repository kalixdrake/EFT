EFT v1 - Roadmap Maestro Multiagente

Objetivo
Orquestar implementación secuencial por agentes, con gates estrictos de calidad para evitar regresiones y asegurar continuidad entre etapas.

Uso operativo con CLI
1. Lee este archivo antes de lanzar un agente.
2. El agente que ejecute una etapa debe actualizar el bloque de estado y el log de ejecución.
3. No iniciar una etapa si la dependencia previa no está en DONE.
4. Cada agente debe ejecutar unit tests de su alcance antes de cerrar.
5. En EFT v1, las migraciones pueden borrarse y rehacerse si eso mejora la organización del dominio.

Reglas Globales (obligatorias para todos los agentes)
No cerrar etapa sin unit tests del alcance en verde.
No cerrar etapa si hay regresiones en tests del módulo afectado.
No ocultar fallos deshabilitando tests.
Todo endpoint tocado debe validar permisos por rol y alcance de datos.
Si hay breaking changes, documentarlos explícitamente en la salida del agente.
Cada agente debe dejar evidencia ejecutable para el siguiente.

Política de Migraciones (EFT v1)
Esta versión permite borrar y rehacer migraciones si mejora consistencia del modelo.
No se requiere compatibilidad histórica de migraciones antiguas.
Cada agente debe:
Regenerar migraciones limpias de su alcance cuando aplique.
Verificar makemigrations y migrate sin errores.
Ejecutar tests posteriores a migraciones.
Si un agente rehace migraciones de otro módulo, debe declararlo en su entrega.

Definition of Done por Etapa (gate de salida)
Una etapa solo puede marcarse DONE si cumple todo:

Criterios funcionales de la etapa cumplidos.
Unit tests nuevos del alcance pasan.
Tests existentes del módulo impactado pasan.
Permisos/roles del alcance validados con pruebas negativas.
Handoff Package completo para el siguiente agente.
Estado de etapa actualizado en este roadmap.

Estado General de Etapas
Etapa	Nombre	Estado	Agente	Inicio	Fin	Notes
0	Arquitectura base y contratos	DONE	Agente-1	2026-04-09	2026-04-09	Contratos RBAC base + handler errores + capacidades /me
1	IAM + RBAC + Alcances	DONE	Agente-1	2026-04-09	2026-04-09	RBAC v2 aplicado en endpoints clave, scopes activos y pruebas negativas
2	Identidad: Usuario/Cliente/Socio/Empleado	DONE	Agente-1	2026-04-09	2026-04-09	Separación Usuario vs Cliente/Socio/Empleado + endpoints y tests de etapa
3	apiUbicaciones	DONE	Agente-1	2026-04-09	2026-04-09	Jerarquía País/Departamento/Ciudad/Ubicación + relaciones por entidad + filtros + integración pedidos
4	apiImpuestos	DONE	Agente-1	2026-04-09	2026-04-09	Modelos/reglas/asignaciones/snapshots + integración en pedidos y conceptos laborales
5	Inventario dual y Activos	DONE	Agente-1	2026-04-09	2026-04-09	ActivoFijo + depreciación/mantenimiento/movimientos + asignación por empleado/ubicación
6	apiDocumentos versionado	DONE	Agente-2	2026-04-10	2026-04-10	apiDocumentos con TipoDocumento/Documento/VersionDocumento/AccesoDocumento, versionado por update y ACL por rol/propietario
7	Hardening de endpoints y permisos	DONE	Agente-2	2026-04-10	2026-04-10	Inventario endpoint-permiso completo + cierre de bypass en custom actions + scoping estricto en querysets
8	apiAuditoria transversal	DONE	Agente-2	2026-04-10	2026-04-10	Auditoría automática por middleware + endpoint de consulta + retención configurable
9	Seeds + contrato frontend de permisos	TODO	-	-	-	-
10	QA seguridad de permisos	TODO	-	-	-	-
Estados válidos: TODO, IN_PROGRESS, BLOCKED, DONE

Secuencia Obligatoria
0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10
No iniciar una etapa si su dependencia previa no está DONE.
Excepción: solo se permite paralelismo si una etapa no comparte archivos ni contratos API con otra.

Contrato de Entrada por Agente (rellenar al iniciar etapa)
STAGE_ID:
STAGE_SCOPE:
DEPENDENCIES_DONE:
KNOWN_CONSTRAINTS:
ACCEPTANCE_CRITERIA:
TEST_COMMANDS:
CHANGED_FILES_ALLOWLIST (opcional):

Contrato de Salida por Agente (obligatorio al finalizar)
Stage Completed
STAGE_ID:
STATUS: DONE o BLOCKED
Resumen:
Implemented Scope
Funcionalidades implementadas:
Endpoints/modelos/servicios afectados:
Files Changed
Archivo:
Motivo:
Migrations
Creadas/rehechas:
Riesgos de datos:
Tests Added or Updated
Test:
Qué valida:
Test Execution Evidence
Comando:
Resultado:
Confirmación no regresión:
Permissions and Security Checks
Reglas aplicadas:
Pruebas negativas realizadas:
Breaking Changes
None o lista:
Known Issues or Follow-ups
Pendientes no bloqueantes:
Next Agent Inputs
Base confiable para continuar:
Riesgos a vigilar:

Plantilla de Checklist por Etapa (copiar dentro de cada etapa)
Scope implementado
Permisos/roles revisados
Unit tests nuevos creados
Unit tests del alcance en verde
Sin regresiones del módulo
Migraciones aplican en limpio
Handoff Package completo
Estado de etapa actualizado en roadmap

Etapa 0 - Arquitectura base y contratos
Objetivo
Definir el rediseño maestro del dominio y los límites entre apps antes de tocar código.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 0
- STAGE_SCOPE: Rediseño maestro del dominio, contratos RBAC, capas de permisos, estándares de errores y contrato de capacidades /me.
- DEPENDENCIES_DONE: []
- KNOWN_CONSTRAINTS: Proyecto EFT v1; se permiten cambios rompientes si mejoran la arquitectura; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Contratos base definidos, errores estandarizados, endpoint /me con capacidades, tests iniciales pasando.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiUsuarios/*, EFT/*, roadmap.md

Reglas Globales (No Negociables)
1. No finalices la etapa si no hay pruebas unitarias relevantes.
2. No finalices la etapa si hay regresiones en pruebas existentes.
3. No modifiques contratos públicos sin documentar impacto y migración.
4. No “silencies” errores de test deshabilitando pruebas.
5. Si detectas deuda técnica crítica previa, repórtala y propón fix mínimo seguro.
6. Todo cambio debe incluir validación de permisos/roles cuando aplique.
7. Si una decisión rompe compatibilidad, puedes borrar las migraciones previas y rehacerlas, el proyecto está en fase inicial.

Flujo de Trabajo Obligatorio
1. Analiza STAGE_SCOPE y mapea archivos/símbolos impactados.
2. Implementa cambios mínimos necesarios.
3. Crea/ajusta unit tests de la etapa.
4. Ejecuta pruebas por capas.
5. Corrige y re-ejecuta hasta pasar.
6. Solo cuando todo pase, genera Handoff Package para el siguiente agente.

Gate de Calidad (Definition of Done)
La etapa SOLO se considera completada si se cumple TODO:
1. ACCEPTANCE_CRITERIA cumplidos.
2. Migraciones aplican correctamente si hubo cambios de modelo.
3. Unit tests nuevos pasan.
4. Tests existentes relevantes pasan sin regresión.
5. Permisos/roles verificados en endpoints impactados.
6. Handoff Package completo y consistente.

Contrato de salida
1. Stage Completed
2. Implemented Scope
3. Files Changed
4. Migrations
5. Tests Added/Updated
6. Test Execution Evidence
7. Permissions & Security Checks
8. Breaking Changes
9. Known Issues / Follow-ups
10. Next Agent Inputs

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 1 - IAM + RBAC + Alcances
Objetivo
Crear núcleo de seguridad escalable para internos por área y jerarquía administrativa.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 1
- STAGE_SCOPE: Implementar IAM dedicado, roles internos, permisos por dominio/acción, alcances OWN/TEAM/DEPARTMENT/COMPANY/GLOBAL e integración con DRF permissions.
- DEPENDENCIES_DONE: [0]
- KNOWN_CONSTRAINTS: El proyecto está en v1 y se permiten cambios rompientes si mejoran la arquitectura.
- ACCEPTANCE_CRITERIA: Roles base, permisos, scopes, object-level permissions y tests por rol/alcance en verde.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiUsuarios/*, EFT/*, roadmap.md

Roles base mínimos
SUPER_ADMIN
ADMIN_GENERAL
AUDITOR
CONTABILIDAD
RRHH
LOGISTICA
COMERCIAL
INVENTARIO
SOPORTE
USUARIO_EXTERNO

Reglas clave
SUPER_ADMIN: acceso total.
ADMIN_GENERAL: acceso operativo total.
CONTABILIDAD: acceso financiero y documental contable/laboral permitido por política.
RRHH: empleados y documentos laborales.
LOGISTICA: pedidos, ubicaciones, inventario operativo.
COMERCIAL: clientes, socios, pedidos comerciales.
AUDITOR: lectura transversal y auditoría.

Alcances de datos
OWN
TEAM
DEPARTMENT
COMPANY
GLOBAL

Criterios de aceptación mínimos
Permisos por acción y recurso funcionando en DRF.
Object-level permissions activas.
Endpoint para capacidades del usuario autenticado.
Tests por rol con casos permitidos y denegados.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 2 - Identidad: Usuario/Cliente/Socio/Empleado
Objetivo
Separar Usuario de entidades de negocio Cliente, Socio y Empleado.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 2
- STAGE_SCOPE: Refactorizar identidades para separar Usuario, Cliente, Socio y Empleado.
- DEPENDENCIES_DONE: [0, 1]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse; mantener compatibilidad solo donde sea estrictamente necesaria.
- ACCEPTANCE_CRITERIA: Nuevos modelos operativos, serializers y viewsets actualizados, migraciones y tests pasando.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiUsuarios/*, roadmap.md

Instrucciones
1. Refactoriza para que Usuario sea identidad técnica.
2. Crea modelos Cliente, Socio y Empleado.
3. Migra datos heredados de rol y perfil_socio al nuevo esquema.
4. Ajusta serializers y viewsets.
5. Mantén compatibilidad temporal solo donde sea estrictamente necesario.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 3 - apiUbicaciones
Objetivo
Implementar apiUbicaciones completa con jerarquía País > Departamento > Ciudad > Ubicación.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 3
- STAGE_SCOPE: Crear modelos de ubicación y relaciones múltiples para clientes, socios y empleados.
- DEPENDENCIES_DONE: [0, 1, 2]
- KNOWN_CONSTRAINTS: El proyecto está en v1; migraciones pueden rehacerse; permisos estrictos por rol.
- ACCEPTANCE_CRITERIA: CRUD completo, filtros, relaciones M2M y tests de reglas de principalidad y permisos.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiUbicaciones/*, apiPedidos/*, roadmap.md

Instrucciones
1. Crea modelos Pais, Departamento, Ciudad, Ubicacion.
2. Crea tablas intermedias para ClienteUbicacion, SocioUbicacion y, si aplica, EmpleadoUbicacion.
3. Integra pedidos para seleccionar ubicación de entrega.
4. Crea filtros por país, departamento, ciudad y tipo.
5. Agrega seeds iniciales geográficos.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 4 - apiImpuestos
Objetivo
Crear modelo de impuestos reutilizable para producto, empresa y empleado.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 4
- STAGE_SCOPE: Crear el modelo Impuesto, reglas de aplicación y snapshots transaccionales.
- DEPENDENCIES_DONE: [0, 1, 2, 3]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Motor de cálculo estable, integración en pedidos y perfiles empleados, tests de cálculo y vigencias.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiImpuestos/*, apiPedidos/*, apiInventario/*, roadmap.md

Instrucciones
1. Crea modelos Impuesto, ReglaImpuesto, AsignacionImpuesto y SnapshotImpuestoTransaccional.
2. Soporta impuestos por tipo de sujeto.
3. Soporta vigencias, prioridad, acumulación y base imponible.
4. Integra cálculo de impuestos en pedidos y en conceptos laborales.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 5 - Inventario dual y Activos
Objetivo
Separar inventario comercial de inventario corporativo.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 5
- STAGE_SCOPE: Crear ActivoFijo y modelos de depreciación/mantenimiento para inventario corporativo.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Dominio de activos funcional, reportes básicos, tests de depreciación, mantenimiento y movimientos.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiInventario/*, roadmap.md

Instrucciones
1. Mantén Producto para venta.
2. Crea ActivoFijo para vehículos, equipos y computadores.
3. Crea CategoriaActivo, DepreciacionActivo, MantenimientoActivo y MovimientoActivo.
4. Define estados y asignación a empleados o ubicaciones.
5. Agrega tests de cálculo, cambios de responsable y alertas.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 6 - apiDocumentos versionado
Objetivo
Implementar documentos para empresa, empleados, clientes y socios con versionado y acceso seguro.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 6
- STAGE_SCOPE: Crear un sistema documental versionado con control de acceso por rol y propietario.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4, 5]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Versionado completo, ACL por área, tests de acceso cruzado y alertas de vencimiento.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiDocumentos/*, roadmap.md

Instrucciones
1. Crea TipoDocumento, Documento, VersionDocumento y AccesoDocumento.
2. Soporta propietarios por tipo.
3. Cada actualización crea una nueva versión.
4. Implementa control de acceso por IAM.
5. Registra descarga y visualización en auditoría.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 7 - Hardening de endpoints y permisos
Objetivo
Revisar todos los endpoints existentes y aplicar validación estricta rol + permiso + alcance.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 7
- STAGE_SCOPE: Inventariar y reforzar permisos de todos los endpoints existentes.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4, 5, 6]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Matriz endpoint-permisos completa, queryset filtering por alcance, pruebas negativas masivas.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: todos los módulos API, roadmap.md

Instrucciones
1. Inventaría todos los endpoints actuales.
2. Define quién puede leer, crear, editar y eliminar cada recurso.
3. Aplica permisos por acción en ViewSets y acciones custom.
4. Implementa filtros de queryset por alcance.
5. Añade pruebas negativas masivas.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 8 - apiAuditoria transversal
Objetivo
Registrar quién accede, modifica, descarga o elimina recursos críticos.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 8
- STAGE_SCOPE: Crear auditoría transversal para accesos y modificaciones sensibles.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4, 5, 6, 7]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Auditoría automática activa, reportes por usuario/acción/recurso, tests de trazabilidad.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: apiAuditoria/*, roadmap.md

Instrucciones
1. Crea modelo de auditoría transversal.
2. Registra usuario, endpoint, acción, recurso, resultado, IP y user-agent.
3. Traza acceso a documentos, empleados, impuestos, pedidos y activos.
4. Crea endpoint de consulta para administradores y auditores.
5. Configura retención y archivado de logs.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 9 - Seeds + contrato frontend de permisos
Objetivo
Dejar ambiente listo para iniciar frontend con usuarios y permisos reales.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 9
- STAGE_SCOPE: Crear seeds, usuarios de ejemplo y contrato de capacidades para frontend.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4, 5, 6, 7, 8]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Proyecto levantable con datos semilla, casos reales por área validados, contrato de permisos listo para UI.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: json/*, apiUsuarios/*, roadmap.md

Instrucciones
1. Crea seeds de roles, permisos, políticas y catálogos base.
2. Crea usuarios de ejemplo por área.
3. Crea endpoint de perfil de capacidades.
4. Crea endpoint de menú por permisos.
5. Ejecuta batería completa de tests.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Etapa 10 - QA seguridad de permisos
Objetivo
Validar que ningún rol accede a más de lo debido y que admin/super admin sí acceden a lo permitido.

Prompt para agente
Eres un agente de desarrollo senior trabajando sobre un proyecto Django/DRF en evolución incremental.

Tu tarea es ejecutar UNA etapa específica del roadmap (la etapa recibida en STAGE_SCOPE) y dejar el sistema listo para que el siguiente agente continúe sin romper lo previo.

Contexto de Entrada Obligatorio
- STAGE_ID: 10
- STAGE_SCOPE: Ejecutar validación final de seguridad de permisos y no regresión funcional.
- DEPENDENCIES_DONE: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- KNOWN_CONSTRAINTS: Se permiten cambios rompientes; migraciones pueden rehacerse.
- ACCEPTANCE_CRITERIA: Reporte de hallazgos, fixes priorizados, re-test final sin hallazgos críticos.
- TEST_COMMANDS: python manage.py test
- CHANGED_FILES_ALLOWLIST: todos los módulos API, roadmap.md

Instrucciones
1. Ejecuta pruebas de caja negra sobre endpoints.
2. Intenta escalamiento horizontal y vertical de privilegios.
3. Verifica que cada rol ve y modifica solo lo permitido.
4. Entrega reporte de brechas con evidencia reproducible.
5. Re-test final sin hallazgos críticos.

Regla de Cierre Forzada
NO cierres esta tarea hasta que los unit tests de tu alcance pasen y exista evidencia de no regresión en los módulos afectados; tu salida debe permitir que el siguiente agente continúe sin pisar funcionalidad rota.

Log de Ejecución (append-only)

Registro
Fecha: 2026-04-09
Etapa: 0
Agente: Agente-1
Acción: Definición de contratos base (RBAC/scopes), estandarización de errores DRF, contrato de capacidades en /api/usuarios/me/, pruebas de etapa 0.
Resultado: DONE
Evidencia test: python manage.py test apiUsuarios.tests_stage0 apiUsuarios.tests_stage1 -v 1 (7/7 OK, USE_SQLITE=true)
Próximo paso: Iniciar Etapa 1 (IAM + RBAC + Alcances) sobre contratos definidos en apiUsuarios/rbac_contracts.py.

Registro
Fecha: 2026-04-09
Etapa: 1
Agente: Agente-1
Acción: Implementación IAM+RBAC+Scopes en capas de permisos DRF y querysets; refuerzo de pruebas con casos negativos.
Resultado: DONE
Evidencia test: python manage.py test -v 1 (29/29 OK, USE_SQLITE=true)
Próximo paso: Etapa 2 (Identidad Usuario/Cliente/Socio/Empleado) usando contrato de capacidades vigente.

Registro
Fecha: 2026-04-09
Etapa: 2
Agente: Agente-1
Acción: Separación de identidad técnica Usuario y creación de entidades Cliente/Socio/Empleado; serializers/viewsets ajustados y compatibilidad temporal mantenida con rol/perfil_socio legado.
Resultado: DONE
Evidencia test: python manage.py test -v 1 (34/34 OK, USE_SQLITE=true)
Próximo paso: Etapa 3 (apiUbicaciones) con relaciones orientadas a Cliente/Socio/Empleado.

Registro
Fecha: 2026-04-09
Etapa: 3
Agente: Agente-1
Acción: Implementación de apiUbicaciones con jerarquía País/Departamento/Ciudad/Ubicación, relaciones ClienteUbicacion/SocioUbicacion/EmpleadoUbicacion, regla de principalidad única, filtros por jerarquía e integración de ubicación de entrega en pedidos.
Resultado: DONE
Evidencia test: python manage.py test apiUsuarios.tests apiUbicaciones.tests apiPedidos.tests apiBancos.tests apiCuentas.tests apiTransacciones.tests -v 1 (30/30 OK, USE_SQLITE=true)
Próximo paso: Etapa 4 (apiImpuestos) sobre el dominio limpio sin legado de roles.

Registro
Fecha: 2026-04-09
Etapa: 4
Agente: Agente-1
Acción: Creación de apiImpuestos con modelos Impuesto/ReglaImpuesto/AsignacionImpuesto/SnapshotImpuestoTransaccional, motor de cálculo por vigencia/prioridad/acumulación/base imponible, integración de impuestos en detalles de pedidos, incorporación de conceptos laborales para empleados y eliminación del legado de porcentaje_impuesto en productos/detalles.
Resultado: DONE
Evidencia test: ejecución focal con Django test runner sin migraciones persistentes (apiImpuestos.tests apiPedidos.tests apiInventario.tests apiUsuarios.tests.test_entity_creation) -> 8/8 OK
Próximo paso: Etapa 5 (Inventario dual y Activos) sobre inventario comercial desacoplado de impuestos directos por campo.

Registro
Fecha: 2026-04-09
Etapa: 5
Agente: Agente-1
Acción: Implementación de inventario dual en apiInventario manteniendo Producto comercial y agregando dominio corporativo de activos con CategoriaActivo, ActivoFijo, DepreciacionActivo, MantenimientoActivo y MovimientoActivo; estados, asignación a empleados/ubicaciones, reportes básicos y endpoints CRUD/filtros.
Resultado: DONE
Evidencia test: ejecución focal con Django test runner sin migraciones persistentes (apiInventario.tests apiPedidos.tests) -> 6/6 OK
Próximo paso: Etapa 6 (apiDocumentos versionado) con propietarios por tipo, control de acceso y versionado por actualización.

Registro
Fecha: 2026-04-10
Etapa: 6
Agente: Agente-2
Acción: Implementación de apiDocumentos con modelos TipoDocumento/Documento/VersionDocumento/AccesoDocumento, validación estricta de propietario por tipo, versionado automático al crear/actualizar archivo, endpoints de visualización/descarga/versiones y trazabilidad de acceso por evento; integración RBAC de recurso DOCUMENTO en matriz de permisos y exposición de rutas API.
Resultado: DONE
Evidencia test: USE_SQLITE=true python manage.py test apiDocumentos.tests apiUsuarios.tests apiInventario.tests apiPedidos.tests -v 1 (18/18 OK)
Próximo paso: Etapa 7 (Hardening de endpoints y permisos) con matriz endpoint-permiso-rol completa y pruebas negativas masivas.

Registro
Fecha: 2026-04-10
Etapa: 7
Agente: Agente-2
Acción: Hardening transversal de permisos con eliminación de bypass en @action, estandarización de guardas RoleScopePermission+roles internos/admin, aplicación de scope_queryset en módulos que carecían de filtro (Usuarios, Ubicaciones, Bancos, Cuentas), validación de alcance en transferencias (cuenta_origen/cuenta_destino) y reemplazo de accesos directos self.queryset/objects.filter por self.get_queryset en acciones sensibles; adicionalmente se creó inventario técnico formal de endpoints y niveles de acceso en EFT/endpoint_permission_matrix.py.
Resultado: DONE
Evidencia test: USE_SQLITE=true python manage.py test apiUsuarios.tests apiInventario.tests apiInventario.tests_stage7 apiPedidos.tests apiTransacciones.tests apiUbicaciones.tests apiBancos.tests apiCuentas.tests apiDocumentos.tests -v 1 (52/52 OK)
Próximo paso: Etapa 8 (apiAuditoria transversal) para consolidar trazabilidad unificada de accesos y mutaciones sensibles.

Registro
Fecha: 2026-04-10
Etapa: 8
Agente: Agente-2
Acción: Creación de apiAuditoria transversal con modelo EventoAuditoria (usuario, endpoint, método, acción, recurso, resultado, código, IP, user-agent y metadata), middleware global de captura automática para endpoints críticos y respuestas 4xx/5xx, endpoint de consulta `/api/auditoria-eventos/` protegido por RBAC (Resources.AUDITORIA), comando de retención/archivado `archivar_eventos_auditoria` con umbral configurable y pruebas de trazabilidad para accesos a documentos y denegaciones de seguridad.
Resultado: DONE
Evidencia test: USE_SQLITE=true python manage.py test apiAuditoria.tests apiDocumentos.tests apiUsuarios.tests apiInventario.tests apiPedidos.tests apiImpuestos.tests apiTransacciones.tests -v 1 (47/47 OK)
Próximo paso: Etapa 9 (Seeds + contrato frontend de permisos) para preparar perfiles/capacidades operativas de UI.

Registro
Fecha: 2026-04-10
Etapa: 9
Agente: Agente-2
Acción: Implementación de contrato frontend en apiUsuarios con endpoint `/api/usuarios/capacidades/` (roles + capabilities) y endpoint `/api/usuarios/menu/` derivado de permisos RBAC; definición de catálogo de menú frontend en `rbac_contracts`; ampliación de comando `cargar_datos_iniciales` con seeds de roles operativos y usuarios de ejemplo por área; incorporación de fixture `json/init_usuarios_permisos_stage9.json` para grupos base.
Resultado: DONE
Evidencia test: .venv/bin/python manage.py test apiUsuarios.tests -v 1 (16/16 OK) y .venv/bin/python manage.py test -v 1 (61/61 OK)
Próximo paso: Etapa 10 (QA seguridad de permisos) con pruebas de caja negra y validación de escalamiento de privilegios.

Registro
Fecha: 2026-04-10
Etapa: 10
Agente: Copilot
Acción: QA de seguridad de permisos con cobertura negativa de escalamiento vertical y lateral en módulos críticos; corrección de brecha RBAC en `get_user_roles` (eliminación de elevación implícita a ADMIN_GENERAL por solo tener entidad Empleado); refuerzo de validación en creación de pedidos para impedir creación lateral en nombre de terceros; incorporación de baterías Stage10 en Usuarios, Pedidos, Transacciones, Documentos, Bancos y Cuentas; entrega de documentación integral de seguridad e integración frontend en `stage10_security_frontend_integration.md`.
Resultado: DONE
Evidencia test: Usuario confirmó ejecución de `USE_SQLITE=true python manage.py test -v 1` con suite completa en verde en Git Bash; etapa cerrada con nuevos escenarios negativos agregados para no-regresión de permisos.
Próximo paso: Monitorear hallazgos de UAT/frontend contra `capabilities` y `menu`, y ampliar pruebas Stage10 a módulos secundarios (Impuestos/Ubicaciones/Auditoría) si se incorporan nuevas acciones sensibles.


## Plan: Tienda RN con RBAC, Dashboards y Chat por Rol

Construir un frontend React Native API-only para e-commerce B2B/B2C sobre el backend actual, reforzando primero el contrato móvil (JWT + bootstrap me/capacidades/menu), y extender backend donde haga falta para: chat IA por rol (prompt segmentado), retiro de la plantilla/ruta HTML legacy de chat, y dashboards internos basados en endpoints existentes. La integración de pagos será in-app con SDK/WebView y tokenización/redirección segura para no almacenar datos sensibles.

**Steps**
1. Fase 0 - Descubrimiento técnico final y contrato API móvil
1.1 Consolidar OpenAPI y matriz RBAC como fuente contractual para frontend móvil: mapear recursos/acciones/scope a pantallas y acciones UI.
1.2 Definir contrato de sesión móvil: login JWT, refresh token, bootstrap con me/capacidades/menu, expiración y renovación silenciosa.
1.3 Cerrar catálogo de acciones sensibles por módulo (pedidos, transacciones, inventario, documentos) y definir comportamiento UI estándar en 401/403/404.

2. Fase 1 - Hardening backend para consumo React Native (bloqueante)
2.1 Implementar autenticación JWT (SimpleJWT) y exponer endpoints de obtención/refresh/verify.
2.2 Configurar DRF para móvil: authentication classes JWT, paginación por defecto y throttling por usuario/IP.
2.3 Configurar CORS/CSRF para app móvil y dominios de API productiva.
2.4 Ajustar documentación OpenAPI para nuevos endpoints de auth/chat v2.

3. Fase 2 - Rediseño backend de chat IA por rol (bloqueante para Chat RN)
3.1 Eliminar interfaz web legacy de chat removiendo la ruta HTML y su template.
3.2 Mantener endpoint API de chat en namespace API (evitar ruta pública fuera de api) y protegerlo con autenticación.
3.3 Evolucionar InteraccionIA para trazabilidad por usuario/rol (FK usuario + rol aplicado + metadata de permisos).
3.4 Integrar prompts por rol usando generar_system_prompt_por_rol y desacoplar prompt hardcoded de procesar_prompt_con_ia.
3.5 Aplicar guardas RBAC dentro del flujo IA: validar acciones sugeridas por IA contra capabilities efectivas del usuario antes de ejecutar tools.
3.6 Versionar endpoint de chat (por ejemplo /api/interacciones/chat/ o /api/v2/chat/) y conservar compatibilidad temporal opcional con feature flag.

4. Fase 3 - Arquitectura React Native (puede iniciar en paralelo con Fase 2 desde contrato)
4.1 Crear app base RN (Expo recomendado para velocidad), módulos de infraestructura: API client, auth store, cache, error boundary, upload manager.
4.2 Implementar capa de red tipada por dominios: usuarios, pedidos, inventario, finanzas, documentos, auditoría, chat.
4.3 Implementar bootstrap post-login: me + capacidades + menu y derivar estado global de permisos.
4.4 Implementar helper can(resource, action) y scope(resource, action) como única fuente de autorización UI.
4.5 Implementar navegación dinámica por menú backend y guards de ruta/pantalla por capability.

5. Fase 4 - UX funcional de tienda virtual por rol
5.1 Clientes/Socios (tienda): catálogo, detalle producto, carrito, checkout, mis pedidos, mis documentos, chat asistido.
5.2 Internos (management): dashboard por rol con KPIs y CTAs de gestión.
5.3 Dashboards mínimos por rol interno (según endpoints existentes):
- ADMIN_GENERAL/SUPER_ADMIN: salud operativa global, aprobaciones pendientes, auditoría reciente.
- LOGISTICA/INVENTARIO: bajo_stock, ajustes, movimientos por producto, estado de pedidos.
- CONTABILIDAD/RRHH: transacciones, programaciones pendientes, nómina pendiente/retrasada.
- AUDITOR: vistas read-only de auditoría, finanzas y documentos sin mutaciones.
5.4 Estandarizar experiencia de errores de permisos: 403 mensaje de autorización, 404 protegido retorna a listado sin revelar existencia.

6. Fase 5 - Checkout y pagos in-app seguros (sin almacenar PAN)
6.1 Definir Payment Orchestrator backend para iniciar pagos con proveedores externos (PSE, MercadoPago, tarjeta tokenizada).
6.2 En móvil usar SDK/WebView oficial del proveedor y recibir callback seguro (deep link + webhook backend).
6.3 Persistir solo metadata no sensible: transaction_id proveedor, estado, referencia interna, monto, timestamps.
6.4 Nunca persistir PAN/CVV ni datos de tarjeta crudos en EFT.
6.5 Implementar reconciliación de estado de pago y actualización de pedido vía endpoint interno.

7. Fase 6 - Chat IA por rol en React Native
7.1 Reemplazar chat único por experiencia segmentada por rol (placeholder, capacidades visibles, disclaimers por alcance).
7.2 Adjuntos en chat con subida multipart y vista de estado de procesamiento.
7.3 Mostrar telemetría de respuesta IA (rol aplicado, acciones permitidas/denegadas) para transparencia y soporte.
7.4 Persistir historial por usuario y paginar conversaciones.

8. Fase 7 - QA, seguridad y release
8.1 Backend: ampliar tests Stage 10 para chat por rol, JWT, acceso no autenticado, y regresión de scope horizontal/vertical.
8.2 Frontend: pruebas unitarias de guards can/scope y pruebas E2E por rol crítico.
8.3 Pruebas de carga sobre endpoints de dashboard y chat.
8.4 Runbook de despliegue: rotación de llaves, variables de entorno, monitoreo y alertas.

**Relevant files**
- c:/Python/Personal/EFT/EFT/urls.py — retirar include legacy de chat y versionar rutas API de interacciones
- c:/Python/Personal/EFT/apiInteracciones/urls.py — eliminar path HTML y exponer endpoint API autenticado
- c:/Python/Personal/EFT/apiInteracciones/templates/chat.html — eliminar plantilla web de chat legacy
- c:/Python/Personal/EFT/apiInteracciones/views/interaccion_view.py — migrar a vista API autenticada con usuario contextual
- c:/Python/Personal/EFT/apiInteracciones/models/interaccion_model.py — agregar trazabilidad por usuario/rol en interacciones
- c:/Python/Personal/EFT/integrations/ai.py — inyectar prompt por rol y guardas de ejecución por capability
- c:/Python/Personal/EFT/integrations/ai_prompts.py — mantener catálogo de prompts por tipo de entidad y políticas
- c:/Python/Personal/EFT/apiUsuarios/permissions.py — reutilizar get_user_roles/build_capabilities/scope_queryset para enforcement IA y frontend contract
- c:/Python/Personal/EFT/apiUsuarios/views/usuario_viewset.py — contrato bootstrap me/capacidades/menu
- c:/Python/Personal/EFT/apiUsuarios/rbac_contracts.py — catálogo de recursos/acciones y menú base
- c:/Python/Personal/EFT/EFT/settings.py — JWT auth classes, paginación, throttling, CORS y settings de seguridad
- c:/Python/Personal/EFT/EFT/endpoint_permission_matrix.py — referencia para dashboards y guardas por endpoint

**Verification**
1. Ejecutar pruebas Stage 10 actuales y agregar suite específica para chat por rol y JWT.
2. Verificar con pruebas por rol que can/scope en frontend coincide con respuestas reales de 403/404 backend.
3. Validar flujo completo móvil: login JWT, refresh, bootstrap, navegación dinámica por menú.
4. Validar hardening chat: usuario externo no ejecuta tools de finanzas internas; auditor solo consulta.
5. Validar adjuntos chat en móvil (PDF/Excel/imagen) y límites de tamaño/tipo.
6. Validar checkout in-app con sandbox de cada proveedor y webhooks de confirmación backend.
7. Confirmar que en base de datos no se almacena PAN/CVV ni payload sensible de tarjeta.
8. Verificar OpenAPI actualizado y colección de pruebas API para equipos frontend/QA.

**Decisions**
- Incluye frontend React Native y backend de soporte (no solo frontend).
- Autenticación móvil objetivo: JWT (access/refresh).
- Pago objetivo: integración in-app con SDK/WebView, tokenización y confirmación por backend.
- Chat IA: una sola superficie de chat, comportamiento/prompt/políticas por rol.
- Seguridad backend es autoridad final; frontend solo refleja capabilities.

**Further Considerations**
1. Elegir estrategia de rollout de chat v2: paralelo con v1 temporal o corte directo con ventana de mantenimiento.
2. Definir proveedor principal de pagos para MVP (MercadoPago vs agregador multi-proveedor) para reducir complejidad inicial.
3. Acordar SLOs de latencia para dashboard y chat antes de optimizar caché/colas.