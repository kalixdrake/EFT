Plan: Arquitectura E-commerce B2B/B2C con Django Bolt
Este plan detalla la construcción y estructuración del backend de tu plataforma de e-commerce impulsada por Django Bolt y tareas asíncronas.

Fases de Desarrollo e Integración

1. Fase Core y Auth (Usuarios y Empleados)
Objetivo: Autenticación base, gestión del personal y perfiles operativos.

 Configurar modelo de usuario personalizado extendiendo AbstractUser en el modelo de Django.
 Implementar sistema de Roles (Cliente, Administrador, Empleado: Almacén/Finanzas/ATC).
 Crear endpoints CRUD para la gestión de Empleados (Crear, listar, editar perfil/rol).
 Implementar lógica de "desactivación" (Soft delete) con flag is_active temporal.
 Configurar serializadores (Django Bolt) para retornos de perfiles parciales (list y detail).
 Configurar Autenticación (JWT sugerido) adaptándolo al estándar asíncrono.
 
2. Fase Catálogo de Productos e Inventario (Stock y Costos)
Objetivo: Manejar ítems, precios, costos, impuestos y campañas promocionales.

 Construir los Modelos Base: Categoria, Producto, Variante (SKU).
 Modelo de Inventario y "Kardex" transaccional (Registro de ENTRADAS y SALIDAS para restock).
 Implementar el tracking de Costo Unitario de Compra que sirva posteriormente para calcular rentabilidad de la orden.
 Crear el modelo Impuesto (configurable por producto y con tasa parametrizable: IVA, Impoconsumo, Exento).
 Crear el modelo OfertaTemporal.
 Endpoint de "Cotización de Producto", donde el modelo calcule de forma en vivo: (Precio Base + Impuestos Base) - Ofertas Activas.
3. Fase Órdenes y Trazabilidad de Ventas
Objetivo: Ciclo de vida completo del carrito de compras hasta su despacho.

 Modelos transaccionales: Carrito, ItemCarrito, Orden, LineaOrden.
 Lógica crítica: Al generar la LineaOrden, crear variables inmutables (snapshot/congelar) del precio histórico de venta, el impuesto cobrado y el costo unitario asumido al momento del checkout.
 Implementar Máquina de Estados para la Orden: Creada -> Pagada -> Preparando -> Enviada -> Entregada -> Cancelada.
 Modelo HistorialOrden para auditoría granular.
 Endpoints para listar órdenes filtradas (Dashboard de Admin) y órdenes propias (Frontend del Cliente).
4. Fase de Integración de Pagos Directos (ePayco)
Objetivo: Recibir pagos con múltiples métodos (PSE, TC, Billeteras).

 Registrar cuenta y obtener credenciales de ePayco.
 Implementar el servicio epayco_service.py con métodos para generar la firma inicial para Checkout.
 Crear endpoint Webhook para recibir notificaciones (IPN - Server to Server) de ePayco.
 Implementar validación de la firma de ePayco (P-Signature validation).
 Lógica de Idempotencia para evitar procesar Webhooks duplicados.
 Al recibir respuesta exitosa, transicionar máquina de estado a Pagada.
5. Fase de Integración de Logística (Envía)
Objetivo: Automatizar la generación de envíos al tener una Orden pagada de forma exitosa.

 Obtener credenciales (usuario/contraseña y token) de la API de Envía.
 Migrar el esquema de Productos a tener peso exacto y dimensiones en el modelo Variante.
 En Event Listener de "Orden transicionó a Pagada", calcular volumétrico total de la orden.
 Implementar el servicio envia_service.py: Función cotizar_envio() y generar_guia().
 Guardar el precio tasado por la transportadora y número de guía PDF en la Orden.
 Endpoint de Webhook de Envía para actualización de estados Enviada y Entregada.
6. Fase de Gestión Financiera (Finanzas & Costos)
Objetivo: Visibilidad total de rentabilidad del e-commerce.

 Crear Modelos corporativos: GastoOperativoMensual, ConfiguracionNomina, HistoricoNomina.
 Generar función de cálculo de Ingreso Neto por Orden: Total Pagado por Cliente - (Sumatoria de Costos Unitarios de los SKU + Valor Etiqueta Envía + Comisión ePayco + Retenciones).
 Desarrollar endpoint analítico (Dashboard de Rentabilidad) contrastando Ganancias del mes vs Dinero Gastado (Nóminas + Gastos Fijos).
 Desarrollar endpoint "Calculadora de Utilidad (Cotizador Rápido)": Recibe Costo de producto (Base o Dinámico), Precio Estimado de Venta y (Opcional) Costo del Flete (vía API Envía o Manual), y retorna el margen de ganancia porcentual y neto instantáneo. Ideal para la interfaz de administrador o al crear nuevos productos para ajustar el precio antes de guardar el SKU en el frontend.
7. Fase de Integración AI: DeepSeek (Logística/Stock)
Objetivo: Asistencia inteligente en decisiones de compra a proveedores y rutas logísticas.

 Configurar un manejador de tareas (Celery/Redis o asíncrono puro de Bolt) para peticiones lentas.
 Crear deepseek_client.py consumiendo API de DeepSeek.
 Diseñar Cronjob que reúne logísticas, stocks actuales y alertas.
 Construir Prompts pidiendo predicciones y estrategias de resurtido estructuradas (JSON).
 Guardar respuestas IA en un ReporteAsesorAi para aprobación final humana.
Verificación y Pruebas Críticas

Ejecutar tests inter-módulos para el controlador del carrito verificando precio final ante rebajas (OfertasTemporales) y cargos obligatorios.
Validar que la factura congela los montos de su momento ignorando aumentos posteriores de precios del origen de BD (Data Mutability Test).
Test de Seguridad Webhooks: Rechazar y mandar error para notificaciones IPN falsas de pasarela simuladas.