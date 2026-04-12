import os
import tempfile

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apiUsuarios.permissions import get_capability_scope
from apiUsuarios.rbac_contracts import Actions, Resources
from integrations.ai import procesar_prompt_con_ia
from integrations.file_processor import procesar_archivo

from ..models import InteraccionIA


@login_required
def chat_view(request):
    if request.method == "GET":
        return render(request, "chat.html")
    return JsonResponse({"error": "Método no permitido"}, status=405)


@require_http_methods(["POST"])
def chat_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Autenticación requerida"}, status=401)
    return JsonResponse(
        {"error": "Endpoint migrado. Use POST /api/interacciones/chat/."},
        status=410,
    )


class InteraccionChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Autenticación requerida"}, status=status.HTTP_401_UNAUTHORIZED)

        scope = get_capability_scope(request.user, Resources.INTERACCION, Actions.CREATE)
        if not scope:
            return Response(
                {"error": "No cuenta con permisos suficientes para usar el chat IA."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_prompt = request.data.get("prompt", "")
        archivo_adjunto = request.FILES.get("archivo")

        if not user_prompt or not str(user_prompt).strip():
            return Response({"error": "Prompt vacío"}, status=status.HTTP_400_BAD_REQUEST)

        contenido_archivo = ""
        nombre_archivo = ""
        archivo_procesado = False

        if archivo_adjunto:
            nombre_archivo = archivo_adjunto.name
            suffix = os.path.splitext(nombre_archivo)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                for chunk in archivo_adjunto.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            try:
                exito, contenido = procesar_archivo(tmp_path)
                if exito:
                    contenido_archivo = contenido
                    archivo_procesado = True
                else:
                    contenido_archivo = f"⚠️ Error al procesar archivo: {contenido}"
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        prompt_final = str(user_prompt).strip()
        if contenido_archivo:
            prompt_final = f"{prompt_final}\n\n[CONTENIDO ADJUNTO]\n{contenido_archivo}"

        resultado = procesar_prompt_con_ia(user=request.user, user_prompt=prompt_final)
        if not resultado.get("ok"):
            if resultado.get("error_code") == "FORBIDDEN_CAPABILITY":
                return Response({"error": resultado["error"]}, status=status.HTTP_403_FORBIDDEN)

            interaccion_error = InteraccionIA.objects.create(
                usuario=request.user,
                usuario_prompt=prompt_final,
                contexto=resultado.get("contexto", ""),
                respuesta_ia=resultado.get("error", "Error al procesar prompt"),
                acciones_ejecutadas="",
                exitosa=False,
            )
            if archivo_adjunto:
                interaccion_error.archivo_adjunto = archivo_adjunto
                interaccion_error.nombre_archivo_original = nombre_archivo
                interaccion_error.save(update_fields=["archivo_adjunto", "nombre_archivo_original"])
            return Response(
                {"error": resultado.get("error", "Error interno del modelo"), "interaccion_id": interaccion_error.id},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        interaccion = InteraccionIA.objects.create(
            usuario=request.user,
            usuario_prompt=prompt_final,
            contexto=resultado.get("contexto", ""),
            respuesta_ia=resultado.get("respuesta", ""),
            acciones_ejecutadas="",
            exitosa=True,
        )
        if archivo_adjunto:
            interaccion.archivo_adjunto = archivo_adjunto
            interaccion.nombre_archivo_original = nombre_archivo
            interaccion.save(update_fields=["archivo_adjunto", "nombre_archivo_original"])

        return Response(
            {
                "respuesta": interaccion.respuesta_ia,
                "interaccion_id": interaccion.id,
                "archivo_guardado": archivo_adjunto is not None,
                "archivo_procesado": archivo_procesado,
                "nombre_archivo": nombre_archivo or None,
            },
            status=status.HTTP_200_OK,
        )
