from __future__ import annotations

import os
from dataclasses import dataclass

import requests

from apiUsuarios.permissions import build_capabilities, get_user_roles

from .ai_prompts import build_system_prompt_for_capabilities


ALLOWED_RESOURCE_CONTEXT_BUILDERS = {}


def _build_inventory_context() -> str:
    from apiInventario.models import Producto

    productos = Producto.objects.filter(activo=True, stock_actual__gt=0).order_by("nombre")[:20]
    if not productos.exists():
        return "No hay productos activos con stock."

    lineas = []
    for producto in productos:
        lineas.append(
            f"- {producto.nombre} (SKU: {producto.sku}) | Precio: {producto.precio_base} | Stock: {producto.stock_actual}"
        )
    return "Productos disponibles:\n" + "\n".join(lineas)


def _build_pedido_context(user) -> str:
    from apiPedidos.models import Pedido
    from apiUsuarios.permissions import get_capability_scope
    from apiUsuarios.rbac_contracts import Actions, Resources, Scopes

    scope = get_capability_scope(user, Resources.PEDIDO, Actions.READ)
    if scope in (Scopes.GLOBAL, Scopes.COMPANY):
        queryset = Pedido.objects.all()
    else:
        queryset = Pedido.objects.filter(cliente=user)

    pedidos = queryset.order_by("-fecha_creacion")[:10]
    if not pedidos.exists():
        return "No hay pedidos visibles para este usuario."

    lineas = []
    for pedido in pedidos:
        lineas.append(
            f"- Pedido #{pedido.id} | Estado: {pedido.estado} | Total: {pedido.total} | Cliente: {pedido.cliente_id}"
        )
    return "Pedidos visibles:\n" + "\n".join(lineas)


def _build_transaccion_context(user) -> str:
    from apiTransacciones.models.transaccion_model import Transaccion
    from apiUsuarios.permissions import get_capability_scope
    from apiUsuarios.rbac_contracts import Actions, Resources, Scopes

    scope = get_capability_scope(user, Resources.TRANSACCION, Actions.READ)
    queryset = Transaccion.objects.select_related("categoria", "cuenta").order_by("-id")
    if scope not in (Scopes.GLOBAL, Scopes.COMPANY):
        queryset = queryset.none()

    transacciones = queryset[:20]
    if not transacciones:
        return "Sin transacciones visibles para este usuario."

    lineas = []
    for transaccion in transacciones:
        lineas.append(
            f"- Tx #{transaccion.id} | Monto: {transaccion.monto} | Cuenta: {transaccion.cuenta_id} | Categoria: {transaccion.categoria_id}"
        )
    return "Transacciones visibles:\n" + "\n".join(lineas)


ALLOWED_RESOURCE_CONTEXT_BUILDERS.update(
    {
        "inventario": _build_inventory_context,
        "pedido": _build_pedido_context,
        "transaccion": _build_transaccion_context,
    }
)


@dataclass(frozen=True)
class AIAccessProfile:
    roles: list[str]
    capabilities: list[dict]

    @property
    def can_chat(self) -> bool:
        return any(
            capability["resource"] == "interaccion" and capability["action"] == "create"
            for capability in self.capabilities
        )


def build_ai_access_profile(user) -> AIAccessProfile:
    return AIAccessProfile(
        roles=sorted(get_user_roles(user)),
        capabilities=build_capabilities(user),
    )


def _collect_context_for_user(user, capabilities: list[dict]) -> str:
    readable_resources = sorted(
        {
            capability["resource"]
            for capability in capabilities
            if capability["action"] == "read" and capability["resource"] in ALLOWED_RESOURCE_CONTEXT_BUILDERS
        }
    )
    if not readable_resources:
        return "El usuario no tiene recursos legibles para contexto."

    bloques = []
    for resource in readable_resources:
        builder = ALLOWED_RESOURCE_CONTEXT_BUILDERS[resource]
        if resource == "inventario":
            content = builder()
        else:
            content = builder(user)
        bloques.append(f"[{resource.upper()}]\n{content}")
    return "\n\n".join(bloques)


def _call_deepseek(messages: list[dict]) -> str:
    api_key = os.getenv("DEEPSEEK_API")
    if not api_key:
        raise RuntimeError("DeepSeek API key no configurada.")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    timeout_seconds = int(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60"))

    response = requests.post(
        f"{base_url}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.1,
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def procesar_prompt_con_ia(*, user, user_prompt: str) -> dict:
    profile = build_ai_access_profile(user)
    if not profile.can_chat:
        return {
            "ok": False,
            "error_code": "FORBIDDEN_CAPABILITY",
            "error": "No cuenta con capacidades para usar el chat IA.",
        }

    contexto_seguro = _collect_context_for_user(user, profile.capabilities)
    system_prompt = build_system_prompt_for_capabilities(
        username=user.username,
        role_labels=profile.roles,
        capabilities=profile.capabilities,
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Contexto disponible:\n{contexto_seguro}"},
        {"role": "user", "content": user_prompt},
    ]

    try:
        respuesta = _call_deepseek(messages)
    except Exception as exc:
        return {
            "ok": False,
            "error_code": "MODEL_ERROR",
            "error": f"Error al consultar el modelo: {exc}",
            "contexto": contexto_seguro,
        }

    return {
        "ok": True,
        "respuesta": respuesta,
        "contexto": contexto_seguro,
        "roles": profile.roles,
        "capabilities": profile.capabilities,
    }
