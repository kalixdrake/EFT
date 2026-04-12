from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from apiInteracciones.models import InteraccionIA
from integrations.ai import procesar_prompt_con_ia
from integrations.file_processor import procesar_archivo

def chat_view(request):
    if request.method == "GET":
        return render(request, 'chat.html')
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@require_http_methods(["POST"])
def chat_api(request):
    """API para procesar prompts con soporte de archivos adjuntos
    
    Los archivos se procesan automáticamente y el contenido se inyecta en el prompt.
    Formatos soportados: PDF, Excel, CSV, Imágenes (JPG, PNG)
    """
    try:
        user_prompt = request.POST.get("prompt", "")
        archivo_adjunto = request.FILES.get("archivo", None)
        
        if not user_prompt:
            return JsonResponse({"error": "Prompt vacío"}, status=400)
        
        # Variables para almacenar información del archivo
        contenido_archivo = ""
        nombre_archivo = ""
        archivo_procesado = False
        
        # Procesar archivo si existe
        if archivo_adjunto:
            nombre_archivo = archivo_adjunto.name
            
            # Guardar archivo temporalmente para procesarlo
            from django.core.files.storage import default_storage
            import tempfile
            import os
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(nombre_archivo)[1]) as tmp_file:
                for chunk in archivo_adjunto.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            try:
                # Procesar el archivo
                exito, contenido = procesar_archivo(tmp_path)
                
                if exito:
                    contenido_archivo = contenido
                    archivo_procesado = True
                else:
                    contenido_archivo = f"⚠️ Error al procesar archivo: {contenido}"
                    archivo_procesado = False
            
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Preparar prompt enriquecido con contenido del archivo
        prompt_final = user_prompt
        if contenido_archivo:
            prompt_final = f"{user_prompt}\n\n[CONTENIDO ADJUNTO]\n{contenido_archivo}"
        
        # Procesamos el prompt con la IA
        resultado = procesar_prompt_con_ia(prompt_final)
        respuesta = resultado.get("respuesta", "Sin respuesta") if isinstance(resultado, dict) else str(resultado)
        interaccion_id = resultado.get("id", None) if isinstance(resultado, dict) else None
        
        # Recuperamos la interacción para guardar el archivo si es necesario
        interaccion = None
        if interaccion_id:
            try:
                interaccion = InteraccionIA.objects.get(id=interaccion_id)
                # Si hay archivo adjunto, lo guardamos
                if archivo_adjunto:
                    interaccion.archivo_adjunto = archivo_adjunto
                    interaccion.nombre_archivo_original = nombre_archivo
                    interaccion.save()
            except InteraccionIA.DoesNotExist:
                pass
        
        if not interaccion:
            # Fallback en caso de que no se haya guardado por alguna razón
            interaccion = InteraccionIA.objects.create(
                usuario_prompt=user_prompt,
                respuesta_ia=respuesta,
                exitosa=True
            )
            if archivo_adjunto:
                interaccion.archivo_adjunto = archivo_adjunto
                interaccion.nombre_archivo_original = nombre_archivo
                interaccion.save()

        return JsonResponse({
            "respuesta": respuesta,
            "interaccion_id": interaccion.id,
            "archivo_guardado": archivo_adjunto is not None,
            "archivo_procesado": archivo_procesado,
            "nombre_archivo": nombre_archivo if nombre_archivo else None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
