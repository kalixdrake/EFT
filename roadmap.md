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
4	apiImpuestos	TODO	-	-	-	-
5	Inventario dual y Activos	TODO	-	-	-	-
6	apiDocumentos versionado	TODO	-	-	-	-
7	Hardening de endpoints y permisos	TODO	-	-	-	-
8	apiAuditoria transversal	TODO	-	-	-	-
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
7. Si una decisión rompe compatibilidad, debe quedar explícita en “Breaking Changes”.

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
