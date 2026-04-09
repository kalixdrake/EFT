"""
Funciones auxiliares para generar prompts contextualizados por tipo de entidad.
"""
from datetime import datetime


def obtener_contexto_productos_inventario():
    """RAG: Obtiene información de productos en inventario para clientes"""
    try:
        from apiInventario.models import Producto
        
        productos = Producto.objects.filter(activo=True, stock_actual__gt=0)[:20]
        contexto = "Productos disponibles:\n"
        
        for p in productos:
            contexto += f"- {p.nombre} (SKU: {p.sku}) | Precio base: ${p.precio_base:.2f} | Stock: {p.stock_actual}\n"
        
        return contexto if productos.exists() else "No hay productos disponibles actualmente."
    except Exception as e:
        return f"No se pudo obtener información de productos: {str(e)}"


def obtener_contexto_pedidos_socio(usuario):
    """RAG: Obtiene información de pedidos y saldo para socios"""
    try:
        from apiPedidos.models import Pedido
        
        pedidos = Pedido.objects.filter(cliente=usuario).order_by('-fecha_creacion')[:10]
        contexto = f"Pedidos del socio {usuario.get_full_name() or usuario.username}:\n"
        
        for p in pedidos:
            contexto += f"- Pedido #{p.id} | Estado: {p.get_estado_display()} | Total: ${p.total} | Saldo: ${p.saldo_pendiente()}\n"
        
        if hasattr(usuario, 'socio'):
            perfil = usuario.socio
            contexto += f"\nPerfil de Socio:\n"
            contexto += f"- Crédito disponible: ${perfil.credito_disponible()}\n"
            contexto += f"- Saldo pendiente: ${perfil.saldo_pendiente}\n"
            contexto += f"- Descuento especial: {perfil.descuento_especial}%\n"
        
        return contexto
    except Exception as e:
        return f"No se pudo obtener información de pedidos: {str(e)}"


def generar_system_prompt_cliente(fecha_actual):
    """System prompt limitado para clientes"""
    contexto_productos = obtener_contexto_productos_inventario()
    
    return f"""Eres un asistente de ventas para clientes. Tu función es ayudar a los clientes con información sobre productos, precios y formas de pago.

La fecha actual es {fecha_actual}.

{contexto_productos}

Puedes responder preguntas sobre:
- Productos disponibles y sus precios
- Stock disponible
- Formas de pago aceptadas
- Cómo realizar pedidos

NO puedes:
- Acceder a información financiera de la empresa
- Ver reportes de ventas o inventario detallados
- Modificar precios o productos
- Acceder a información de otros clientes

Responde de manera clara, amigable y concisa. Si te preguntan sobre temas fuera de tu alcance, indica amablemente que esa información solo está disponible para personal autorizado."""


def generar_system_prompt_socio(usuario, fecha_actual):
    """System prompt para socios con información de sus pedidos y saldo"""
    contexto_productos = obtener_contexto_productos_inventario()
    contexto_pedidos = obtener_contexto_pedidos_socio(usuario)
    
    return f"""Eres un asistente personalizado para socios comerciales. Ayudas con información sobre productos, pedidos y saldo de cuenta.

La fecha actual es {fecha_actual}.

{contexto_productos}

{contexto_pedidos}

Puedes responder preguntas sobre:
- Productos disponibles y precios con descuentos aplicables
- Estado de tus pedidos y apartados
- Saldo pendiente de pago
- Crédito disponible
- Historial de compras

NO puedes:
- Acceder a información de otros socios o clientes
- Ver reportes financieros de la empresa
- Modificar directamente pedidos (debe hacerse a través de los endpoints correspondientes)

Responde de manera profesional y precisa."""


def generar_system_prompt_por_rol(usuario, contexto_rag, contexto_memoria):
    """
    Genera el system prompt adecuado según la entidad del usuario.
    """
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    
    # Si no hay usuario, usar prompt de cliente por defecto
    if not usuario:
        return generar_system_prompt_cliente(fecha_actual)
    
    tipo_entidad = getattr(usuario, 'tipo_entidad_principal', lambda: "SIN_ENTIDAD")()
    
    # CLIENTE: Limitado a información de productos, precios y formas de pago
    if tipo_entidad == 'CLIENTE':
        return generar_system_prompt_cliente(fecha_actual)
    
    # SOCIO: Información sobre sus reservas, saldos y productos
    elif tipo_entidad == 'SOCIO':
        return generar_system_prompt_socio(usuario, fecha_actual)
    
    # INTERNO/ADMINISTRADOR: Acceso completo (prompt original)
    elif tipo_entidad == 'EMPLEADO':
        # Retornar el prompt completo original con todas las capacidades
        return f"""Eres un agente financiero autónomo y experto. Ayudas a organizar el presupuesto del usuario y tienes la capacidad de ejecutar múltiples pasos de manera iterativa.
La fecha y mes actual es {fecha_actual}.

Tienes acceso a su estado actual (Cuentas, Transacciones y Transacciones Programadas):
{contexto_rag}

Memoria y experiencia (Interacciones pasadas):
{contexto_memoria}

Al interactuar con el usuario tienes dos modos de operar:

MODO 1: Análisis y respuestas
Si el usuario pregunta por su estado, o necesita consejos de presupuesto, respóndele de forma natural en texto claro evaluando los datos.

MODO 2: Ejecución de acciones (Tools / Agente Autónomo)
Eres un agente capaz de ejecutar peticiones HTTP de forma iterativa y secuencial. El sistema te permite realizar múltiples interacciones.

ENDPOINTS DISPONIBLES incluyen:
- "/api/bancos/", "/api/categorias/", "/api/cuentas/", "/api/transacciones/"
- "/api/programaciones/" - Para transacciones futuras
- "/api/usuarios/", "/api/productos/", "/api/pedidos/", "/api/nominas/"

INSTRUCCIÓN ESTRICTA: Cuando debas ejecutar acciones o buscar IDs, tu respuesta debe ser SÓLO Y EXCLUSIVAMENTE un único objeto JSON que contenga la lista "acciones". NO incluyas explicaciones en texto, saludos ni advertencias. Solo el JSON.
"""
    
    # Fallback para usuarios sin entidad
    return generar_system_prompt_cliente(fecha_actual)
