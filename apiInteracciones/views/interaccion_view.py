from django.shortcuts import render
from django.http import JsonResponse
import json
from apiInteracciones.models import InteraccionIA
from integrations.ai import procesar_prompt_con_ia

def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_prompt = data.get("prompt", "")
            if not user_prompt:
                return JsonResponse({"error": "Prompt vacío"}, status=400)
                
            # Procesamos el prompt
            resultado = procesar_prompt_con_ia(user_prompt)
            respuesta = resultado.get("respuesta", "Sin respuesta") if isinstance(resultado, dict) else str(resultado)
            
            return JsonResponse({"respuesta": respuesta})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return render(request, 'chat.html')
