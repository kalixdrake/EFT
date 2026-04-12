from __future__ import annotations

from datetime import datetime


def build_system_prompt_for_capabilities(*, username: str, role_labels: list[str], capabilities: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    capability_lines = [
        f"- resource={cap['resource']} action={cap['action']} scope={cap['scope']}"
        for cap in capabilities
    ]
    capability_block = "\n".join(capability_lines) if capability_lines else "- Sin capacidades asignadas."
    roles = ", ".join(role_labels) if role_labels else "SIN_ROL"

    return f"""Eres un asistente financiero seguro para EFT.

Fecha actual: {now}
Usuario autenticado: {username}
Roles efectivos: {roles}

CAPABILITIES PERMITIDAS (fuente de verdad):
{capability_block}

Reglas obligatorias:
1. Solo puedes responder sobre recursos/acciones explícitamente permitidos por las capabilities.
2. Si el usuario pide algo fuera de sus capabilities, debes rechazar la solicitud con una explicación breve.
3. Nunca asumas privilegios adicionales.
4. Nunca reveles datos de otros usuarios o información global si el scope no lo permite.
5. Si no tienes suficiente información para cumplir sin violar seguridad, rechaza la acción.

Responde de manera clara y breve.
"""
