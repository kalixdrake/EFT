from __future__ import annotations

from typing import Any

from .models import EventoAuditoria


CRITICAL_RESOURCES = {"documento", "user", "impuesto", "pedido", "inventario"}
CRITICAL_ENDPOINT_PREFIXES = (
    "/api/documentos",
    "/api/usuarios",
    "/api/empleados",
    "/api/clientes",
    "/api/socios",
    "/api/impuestos",
    "/api/reglas-impuesto",
    "/api/asignaciones-impuesto",
    "/api/pedidos",
    "/api/productos",
    "/api/activos-fijos",
    "/api/movimientos-inventario",
    "/api/movimientos-activo",
    "/api/depreciaciones-activo",
    "/api/mantenimientos-activo",
)


def should_audit(request, response) -> bool:
    path = request.path or ""
    if request.method == "OPTIONS":
        return False
    if any(path.startswith(prefix) for prefix in CRITICAL_ENDPOINT_PREFIXES):
        return True
    resource = getattr(getattr(request, "resolver_match", None), "kwargs", {}).get("resource")
    if resource in CRITICAL_RESOURCES:
        return True
    return 400 <= response.status_code < 600


def resolve_action(request, response) -> str:
    if hasattr(response, "renderer_context"):
        view = response.renderer_context.get("view")
        if view and getattr(view, "action", None):
            return view.action
    return request.method.lower()


def resolve_resource(request, response) -> str:
    if hasattr(response, "renderer_context"):
        view = response.renderer_context.get("view")
        if view and getattr(view, "rbac_resource", None):
            return view.rbac_resource
    path = request.path or ""
    for segment in path.split("/"):
        if segment:
            return segment
    return "unknown"


def _safe_metadata(request, response) -> dict[str, Any]:
    data = {
        "query_params": dict(request.GET.items()),
        "path": request.path,
        "view_name": getattr(getattr(request, "resolver_match", None), "view_name", ""),
    }
    if hasattr(response, "data") and isinstance(response.data, dict):
        keys = [str(k) for k in response.data.keys()][:25]
        data["response_keys"] = keys
    return data


def persist_audit_event(request, response) -> None:
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    status_code = int(getattr(response, "status_code", 500))
    if status_code in (401, 403):
        result = EventoAuditoria.ResultadoEvento.FORBIDDEN
    elif status_code >= 400:
        result = EventoAuditoria.ResultadoEvento.ERROR
    else:
        result = EventoAuditoria.ResultadoEvento.SUCCESS

    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")

    EventoAuditoria.objects.create(
        usuario=user,
        endpoint=request.path,
        metodo_http=request.method,
        accion=resolve_action(request, response),
        recurso=resolve_resource(request, response),
        resultado=result,
        codigo_estado=status_code,
        ip_origen=ip or None,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        metadata=_safe_metadata(request, response),
    )

