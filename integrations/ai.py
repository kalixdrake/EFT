import os
import sys
import json
import django
from datetime import datetime

try:
    from llama_cpp import Llama
except Exception:
    Llama = None

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_env_file(path):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            for raw_line in file_handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"").strip("'")
                if key:
                    os.environ.setdefault(key, value)
    except OSError:
        pass

_load_env_file(os.path.join(BASE_DIR, ".env"))

# 1. Configurar Django para poder usar los modelos/endpoints desde el script
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EFT.settings')
django.setup()

# Importar los modelos necesarios
from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.models.programacion_model import ProgramacionTransaccion
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer
from apiTransacciones.serializers.transferencia_serializer import TransferenciaSerializer
from apiTransacciones.serializers.programacion_serializer import ProgramacionTransaccionSerializer

from apiCuentas.models.cuenta_model import Cuenta
from apiBancos.models.banco_model import Banco

from apiInteracciones.models import InteraccionIA

def obtener_historial_transacciones():
    """RAG: Obtiene las transacciones recientes y el estado de cuentas para darle contexto a la IA."""
    try:
        # Obtener resumen de cuentas
        cuentas = Cuenta.objects.all()
        resumen_cuentas = "Cuentas actuales:\n"
        for c in cuentas:
            nombre_cuenta = f" | Nombre: {c.nombre}" if c.nombre else ""
            resumen_cuentas += f"- ID: {c.id} | Banco: {c.banco.nombre}{nombre_cuenta} | Saldo: ${c.saldo}\n"

        # Obtener transacciones
        transacciones = Transaccion.objects.all().order_by('-id')[:30]
        historial = "Últimas transacciones:\n"
        for t in transacciones:
            tipo_nombre = "EGRESO" if t.categoria and t.categoria.egreso else "INGRESO"
            cuenta = f"{t.cuenta.id}" if t.cuenta else "N/A"
            fecha_ejecucion = t.fecha_ejecucion.strftime('%Y-%m-%d') if t.fecha_ejecucion else "N/A"
            historial += f"- {fecha_ejecucion} | Desc: {t.descripcion} | Monto: ${t.monto} | Tipo: {tipo_nombre} | Cuenta: {cuenta}\n"

        # Obtener programaciones futuras
        programaciones = ProgramacionTransaccion.objects.filter(
            estado='PENDIENTE',
            activa=True
        ).order_by('fecha_programada')[:20]
        resumen_programadas = "\nTransacciones programadas (pendientes):\n"
        for p in programaciones:
            fecha_programada = p.fecha_programada.strftime('%Y-%m-%d')
            resumen_programadas += (
                f"- {fecha_programada} | Desc: {p.descripcion} | Monto: ${p.monto} | "
                f"Frecuencia: {p.frecuencia} | Cuenta: {p.cuenta.id} | Categoria: {p.categoria.nombre}\n"
            )
        
        return f"{resumen_cuentas}\n{historial}{resumen_programadas}"
    except Exception as e:
        return f"Error al obtener historial: {str(e)}"

def crear_cuenta(datos):
    """Crea un banco si no existe y luego una cuenta."""
    try:
        nombre_banco = datos.get('banco_nombre', 'Banco Desconocido')
        saldo = datos.get('saldo_inicial', 0.0)
        numero = datos.get('numero')
        nombre_cuenta = datos.get('nombre')
        
        banco, created = Banco.objects.get_or_create(nombre=nombre_banco)
        cuenta = Cuenta.objects.create(
            banco=banco,
            saldo=saldo,
            numero=numero,
            nombre=nombre_cuenta
        )
        
        return {"status": "success", "message": f"Cuenta ID {cuenta.id} creada en {banco.nombre} con saldo inicial de ${saldo}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear cuenta: {str(e)}"}

def crear_transaccion(datos):
    """Crea una transacción inmediata en la base de datos."""
    try:
        cuenta_id = datos.get('cuenta_id') or datos.get('cuenta')
        categoria_id = datos.get('categoria_id') or datos.get('categoria')
        monto = datos.get('monto')
        descripcion = datos.get('descripcion')
        fecha_ejecucion = datos.get('fecha_ejecucion')

        if not cuenta_id or not categoria_id:
            return {"status": "error", "message": "Se requiere 'cuenta' y 'categoria' para crear una transacción."}

        if not monto or not descripcion:
            return {"status": "error", "message": "Se requiere 'monto' y 'descripcion' para crear una transacción."}

        if fecha_ejecucion is None:
            fecha_ejecucion = datetime.now().strftime("%Y-%m-%d")

        payload = {
            "cuenta": cuenta_id,
            "categoria": categoria_id,
            "monto": monto,
            "descripcion": descripcion,
            "fecha_ejecucion": fecha_ejecucion,
        }

        serializer = TransaccionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        transaccion = serializer.save()

        return {
            "status": "success",
            "message": f"Transacción ID {transaccion.id} creada por ${transaccion.monto} ('{transaccion.descripcion}')."
        }
    except Exception as e:
        return {"status": "error", "message": f"Error al crear transacción: {str(e)}"}

def crear_programacion(datos):
    """Crea una transacción programada/futura en la base de datos."""
    try:
        cuenta_id = datos.get('cuenta_id') or datos.get('cuenta')
        categoria_id = datos.get('categoria_id') or datos.get('categoria')
        monto = datos.get('monto')
        descripcion = datos.get('descripcion')
        fecha_programada = datos.get('fecha_programada')
        frecuencia = datos.get('frecuencia', 'UNICA')
        fecha_fin_repeticion = datos.get('fecha_fin_repeticion')

        if not cuenta_id or not categoria_id:
            return {"status": "error", "message": "Se requiere 'cuenta' y 'categoria' para crear una programación."}
        if not monto or not descripcion or not fecha_programada:
            return {"status": "error", "message": "Se requiere 'monto', 'descripcion' y 'fecha_programada'."}

        payload = {
            "cuenta": cuenta_id,
            "categoria": categoria_id,
            "monto": monto,
            "descripcion": descripcion,
            "fecha_programada": fecha_programada,
            "frecuencia": frecuencia,
        }
        if frecuencia != 'UNICA' and not fecha_fin_repeticion:
            return {"status": "error", "message": "Se requiere 'fecha_fin_repeticion' para programaciones recurrentes."}
        if frecuencia != 'UNICA':
            payload["fecha_fin_repeticion"] = fecha_fin_repeticion

        serializer = ProgramacionTransaccionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        programacion = serializer.save()

        return {
            "status": "success",
            "message": f"Programación ID {programacion.id} creada para {programacion.fecha_programada}."
        }
    except Exception as e:
        return {"status": "error", "message": f"Error al crear programación: {str(e)}"}

def crear_transferencia(datos):
    """Crea una transferencia inmediata entre cuentas como doble transacción."""
    try:
        cuenta_origen_id = datos.get('cuenta_origen_id') or datos.get('cuenta_origen')
        cuenta_destino_id = datos.get('cuenta_destino_id') or datos.get('cuenta_destino')
        monto = datos.get('monto')
        descripcion = datos.get('descripcion')
        fecha_ejecucion = datos.get('fecha_ejecucion')

        if not cuenta_origen_id or not cuenta_destino_id:
            return {"status": "error", "message": "Se requiere 'cuenta_origen' y 'cuenta_destino'."}
        if not monto or not descripcion:
            return {"status": "error", "message": "Se requiere 'monto' y 'descripcion'."}

        payload = {
            "cuenta_origen": cuenta_origen_id,
            "cuenta_destino": cuenta_destino_id,
            "monto": monto,
            "descripcion": descripcion,
            "fecha_ejecucion": fecha_ejecucion,
        }

        serializer = TransferenciaSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return {
            "status": "success",
            "message": "Transferencia creada exitosamente."
        }
    except Exception as e:
        return {"status": "error", "message": f"Error al crear transferencia: {str(e)}"}

def obtener_memoria_ia():
    try:
        interacciones = InteraccionIA.objects.all().order_by('-fecha')[:5]
        if not interacciones:
            return "No hay interacciones previas."
        
        memoria = "Historial de interacciones previas con el usuario (aprende de aqui):\n"
        for i in reversed(interacciones):
            memoria += f"Usuario: {i.usuario_prompt}\nAplicaste acciones: {i.acciones_ejecutadas}\nFue exitosa: {i.exitosa}\n\n"
        return memoria
    except Exception as e:
        return f"Error al obtener memoria: {e}"

def _get_deepseek_config():
    api_key = (
        os.getenv("deepseek_API")
    )
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    timeout_seconds = 60
    return api_key, base_url, model, timeout_seconds

def _get_usage_mode():
    usage = os.getenv("usage") or os.getenv("USAGE")
    if not usage:
        return None
    usage = usage.strip().lower()
    if usage in ("local", "online"):
        return usage
    return None

def _call_deepseek(messages, temperature=0.7):
    api_key, base_url, model, timeout_seconds = _get_deepseek_config()
    if not api_key:
        raise RuntimeError("DeepSeek API key no configurada.")

    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

def _init_llm_provider(model_path):
    api_key, _, _, _ = _get_deepseek_config()
    usage = _get_usage_mode()
    if usage == "online":
        if api_key:
            return {"type": "deepseek"}
        return {"type": "none", "error": "usage=online pero falta deepseek_API."}
    if usage == "local":
        if Llama is None:
            return {
                "type": "none",
                "error": "usage=local pero llama_cpp no esta disponible.",
            }
        if not os.path.exists(model_path):
            return {
                "type": "none",
                "error": f"No se encontro el modelo local en {model_path}.",
            }
        return {
            "type": "local",
            "llm": Llama(
                model_path=model_path,
                n_gpu_layers=-1,
                seed=1337,
                n_ctx=16384,
                verbose=False,
            ),
        }
    if api_key:
        return {"type": "deepseek"}
    if Llama is None:
        return {
            "type": "none",
            "error": "No hay API key de DeepSeek y llama_cpp no esta disponible.",
        }
    if not os.path.exists(model_path):
        return {
            "type": "none",
            "error": f"No se encontro el modelo local en {model_path}.",
        }
    return {
        "type": "local",
        "llm": Llama(
            model_path=model_path,
            n_gpu_layers=-1,
            seed=1337,
            n_ctx=10240,
            verbose=False,
        ),
    }

def _get_backend_base_url():
    return os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

def procesar_prompt_con_ia(user_prompt):
    model_path = "./llms/Qwen3.5-4B.Q4_K_M.gguf"

    provider = _init_llm_provider(model_path)
    if provider["type"] == "none":
        return {"respuesta": provider["error"], "id": None}

    # Usar RAG (Generación Aumentada por Recuperación)
    contexto_rag = obtener_historial_transacciones()
    contexto_memoria = obtener_memoria_ia()

    if provider["type"] == "local":
        print("Cargando el modelo local...")

    actual_date = datetime.now()
    
    system_prompt = f"""Eres un agente financiero autónomo y experto. Ayudas a organizar el presupuesto del usuario y tienes la capacidad de ejecutar múltiples pasos de manera iterativa.
La fecha y mes actual es {actual_date.strftime('%Y-%m-%d')}.

Tienes acceso a su estado actual (Cuentas, Transacciones y Transacciones Programadas):
{contexto_rag}

Memoria y experiencia (Interacciones pasadas):
{contexto_memoria}

Al interactuar con el usuario tienes dos modos de operar:

MODO 1: Análisis y respuestas
Si el usuario pregunta por su estado, o necesita consejos de presupuesto, respóndele de forma natural en texto claro evaluando los datos.

MODO 2: Ejecución de acciones (Tools / Agente Autónomo)
Eres un agente capaz de ejecutar peticiones HTTP de forma iterativa y secuencial. El sistema te permite realizar múltiples interacciones.
Si el usuario te pide registrar una operación o varias, PUEDES y DEBES dividir las tareas en varios pasos si no conoces los IDs.
Por ejemplo, si no sabes el ID de una cuenta o categoría:
1. Responde ÚNICAMENTE con un JSON que contenga las acciones "GET".
2. EL SISTEMA SE PAUSARÁ, ejecutará esas llamadas por ti, y te devolverá los resultados exactos.
3. Luego, CONOCIENDO los IDs devueltos por el sistema, respondes con un nuevo JSON ejecutando los "POST", "PUT", etc.

NUNCA asumas IDs, ni pidas disculpas diciendo "no puedo hacer llamadas secuenciales", porque SÍ puedes. Está completamente diseñado para que operes en pasos lógicos.
SIEMPRE que uses el modo de acciones, tu respuesta debe ser ÚNICAMENTE un objeto JSON válido (sin texto extra fuera de él).

REGLA IMPORTANTE PARA TRANSACCIONES FUTURAS: Si el usuario indica que "debe realizar" un movimiento, "tiene una deuda", "tiene que hacer un pago", o se refiere a un gasto o ingreso en el futuro, ESTO NO ES UNA TRANSACCIÓN NORMAL. DEBES registrarlo como una Transacción Programada llamando al POST de "/api/programaciones/". Utiliza el POST de "/api/transacciones/" ÚNICAMENTE para movimientos que ya ocurrieron o se efectúan en este preciso momento.

ENDPOINTS DISPONIBLES (FORMATO REFACTORIZADO):

A) ENDPOINTS DE DOCUMENTACION
- GET "/api/schema/": Devuelve OpenAPI en JSON. Si tienes dudas del payload o de un campo, usa este endpoint primero.
- GET "/api/docs/": UI de Swagger (referencia visual; normalmente preferir "/api/schema/" porque retorna JSON).

B) ENDPOINTS BASICOS (PATRON CRUD)
Para los recursos que se listan abajo, asume este patron:
- GET "/api/{{recurso}}/" -> listar (usa filtros cuando existan)
- POST "/api/{{recurso}}/" -> crear
- GET "/api/{{recurso}}/{{id}}/" -> detalle
- PATCH "/api/{{recurso}}/{{id}}/" -> actualizar parcial
- DELETE "/api/{{recurso}}/{{id}}/" -> eliminar

Recursos base:
1. "/api/bancos/"
    - Filtro recomendado en GET: "nombre"
    - POST esperado: {{"nombre": "string"}}

2. "/api/categorias/"
    - Filtros disponibles en GET: "egreso"
    - POST esperado: {{"nombre": "string", "descripcion": "string", "egreso": true}}

3. "/api/cuentas/"
    - Filtros recomendados en GET: "nombre", "banco"
    - POST esperado: {{"banco": 1, "saldo": 1000.0, "numero": 1234, "nombre": "Opcional"}}
    - IMPORTANTE: "banco" siempre es ID numerico

4. "/api/transacciones/"
    - Filtros disponibles en GET: "fecha_min", "fecha_max", "monto_min", "monto_max", "descripcion", "categoria", "cuenta", "from_programacion"
    - POST esperado: {{
         "monto": 150.0,
         "descripcion": "string",
         "categoria": 2,
         "cuenta": 1,
                 "fecha_ejecucion": "2026-03-27T10:00:00Z"
      }}
        - IMPORTANTE: la fecha no puede ser futura. Para hechos FUTUROS usa programaciones.

5. "/api/programaciones/"
    - Filtros disponibles en GET: "fecha_min", "fecha_max", "monto_min", "monto_max", "descripcion", "categoria", "cuenta", "estado", "frecuencia", "activa"
    - POST esperado: {{
         "monto": 100.0,
         "descripcion": "string",
         "categoria": 2,
         "cuenta": 1,
         "fecha_programada": "2026-04-15T10:00:00Z",
         "frecuencia": "UNICA",
         "fecha_fin_repeticion": "2026-12-15T10:00:00Z"
      }}
    - IMPORTANTE: si "frecuencia" != "UNICA" debes incluir "fecha_fin_repeticion".
    - IMPORTANTE: "fecha_programada" debe ser futura.

C) ACCIONES PERSONALIZADAS (NO CRUD)
0. POST "/api/transacciones/transferir/"
    - Registra una transferencia real entre cuentas como dos transacciones (egreso e ingreso)
    - Payload esperado: {{
         "monto": 150.0,
         "descripcion": "string",
         "cuenta_origen": 1,
         "cuenta_destino": 2,
         "fecha_ejecucion": "2026-03-27T10:00:00Z" (opcional)
      }}
    - NOTA: Aunque el schema pueda listar un objeto Transaccion, este endpoint usa cuenta_origen y cuenta_destino.

1. GET "/api/programaciones/pendientes/"
    - Lista programaciones pendientes y activas (acepta los mismos filtros que /api/programaciones/)

2. GET "/api/programaciones/activas/"
    - Lista programaciones activas (acepta los mismos filtros que /api/programaciones/)

3. POST "/api/programaciones/{id}/activar/"
    - Activa una programación

4. POST "/api/programaciones/{id}/desactivar/"
    - Desactiva una programación

5. POST "/api/programaciones/{id}/cancelar/"
    - Cancela una programación (no ejecutada)

6. POST "/api/programaciones/{id}/ejecutar/"
    - Ejecuta una transacción programada y genera la transacción real

7. GET "/api/programaciones/presupuesto-consolidado/"
    - Devuelve el presupuesto consolidado por cuenta
    - Query params: "cuentas" (repetible, IDs de cuentas). Ej: ?cuentas=1&cuentas=2

Ejemplo de respuesta en un paso de tu ejecución:
{{
  "acciones": [
    {{
            "endpoint": "/api/categorias/",
      "method": "GET"
    }},
    {{
      "endpoint": "/api/cuentas/",
      "method": "GET",
      "data": {{"nombre": "Ahorros"}}
    }}
  ]
}}

INSTRUCCIÓN ESTRICTA: Cuando debas ejecutar acciones o buscar IDs, tu respuesta debe ser SÓLO Y EXCLUSIVAMENTE un único objeto JSON que contenga la lista "acciones". NO incluyas explicaciones en texto, saludos ni advertencias. Solo el JSON.
Además, REGLA IMPORTANTE DE EFICIENCIA: Siempre que vayas a realizar acciones de tipo GET, y consideres que es posible utilizar filtros (como fecha, categoria, nombre, etc. según se te expuso antes), USALOS. Para fechas usa ISO-8601 (ej: 2026-03-27T10:00:00Z). Para consultas de programaciones prioriza filtrar por "categoria" antes que por "descripcion" cuando la categoria sea deducible; si debes filtrar por "descripcion", usa UNA palabra clave en lugar de un texto largo. El objetivo es mantener las peticiones y respuestas lo más pequeñas y precisas posibles.
REGLA DE CONSULTA DE DOCUMENTACION: No llames "/api/schema/" en cada solicitud. Usalo solo cuando tengas duda real del contrato de un endpoint, y luego continúa con llamadas filtradas y específicas.
"""
    
    print(f"\n[Usuario]: {user_prompt}\n")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    MAX_ITERATIONS = 20
    for iteracion in range(MAX_ITERATIONS):
        try:
            if provider["type"] == "deepseek":
                respuesta_ia = _call_deepseek(messages, temperature=0.1)
            else:
                output = provider["llm"].create_chat_completion(
                    messages=messages,
                    temperature=0.1,
                    repeat_penalty=1.1,
                )
                respuesta_ia = output["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error al consultar el modelo: {e}")
            interaccion_id = None
            try:
                interaccion = InteraccionIA.objects.create(
                    usuario_prompt=user_prompt,
                    contexto=contexto_rag,
                    respuesta_ia="Error al consultar el modelo.",
                    acciones_ejecutadas="",
                    exitosa=False,
                )
                interaccion_id = interaccion.id
            except Exception:
                pass
            return {"respuesta": "Error al consultar el modelo.", "id": interaccion_id}
        messages.append({"role": "assistant", "content": respuesta_ia})

        # Intentar interpretar la respuesta como una o más acciones JSON
        try:
            start_idx = respuesta_ia.find("{")
            end_idx = respuesta_ia.rfind("}")
            
            acciones_a_ejecutar = []
            
            if start_idx != -1 and end_idx != -1:
                json_str = respuesta_ia[start_idx:end_idx+1]
                try:
                    datos = json.loads(json_str)
                    if "acciones" in datos:
                        acciones_a_ejecutar = datos["acciones"]
                    elif "action" in datos:
                        acciones_a_ejecutar.append({
                            "endpoint": datos["action"],
                            "method": "POST",
                            "data": {k: v for k, v in datos.items() if k != "action"}
                        })
                except json.JSONDecodeError:
                    for line in json_str.split('\n'):
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                d = json.loads(line)
                                if "acciones" in d:
                                    acciones_a_ejecutar.extend(d["acciones"])
                                elif "action" in d:
                                    acciones_a_ejecutar.append({
                                        "endpoint": d["action"],
                                        "method": "POST",
                                        "data": {k: v for k, v in d.items() if k != "action"}
                                    })
                            except json.JSONDecodeError:
                                pass
                                
            if acciones_a_ejecutar:
                print(f"\n[IA (Paso {iteracion+1})]: Resumen de acciones a realizar:")
                for i, accion in enumerate(acciones_a_ejecutar, 1):
                    print(f"  {i}. {accion.get('method', 'POST')} a {accion.get('endpoint')} -> {accion.get('data', {})}")
                    
                print(f"\n[IA (Paso {iteracion+1})]: Ejecutando llamadas a la API...")
                
                resultados_para_ia = []
                for accion in acciones_a_ejecutar:
                    endpoint = accion.get("endpoint")
                    method = accion.get("method", "POST").upper()
                    payload = accion.get("data", {})
                    
                    base_url = _get_backend_base_url().rstrip("/")
                    normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
                    url = f"{base_url}{normalized_endpoint}"
                    print(f"-> Llamando a {method} {endpoint}...")
                    
                    try:
                        if method == "POST":
                            response = requests.post(url, json=payload, timeout=5)
                        elif method == "GET":
                            response = requests.get(url, params=payload, timeout=5)
                        elif method == "PUT":
                            response = requests.put(url, json=payload, timeout=5)
                        elif method == "PATCH":
                            response = requests.patch(url, json=payload, timeout=5)
                        elif method == "DELETE":
                            response = requests.delete(url, timeout=5)
                        else:
                            error_msg = f"Error: Método HTTP {method} no soportado."
                            print(f"   [{error_msg}]\n")
                            resultados_para_ia.append(error_msg)
                            continue
                            
                        print(f"   [Éxito] Resp {response.status_code}: {response.text}\n")
                        resultados_para_ia.append(f"Result for {method} {endpoint}: Status {response.status_code}, Body: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"   [Excepción] Error al conectar con {endpoint}: {e}\n")
                        resultados_para_ia.append(f"Error for {method} {endpoint}: {e}")
                
                # Le pasamos los resultados a la IA para que continúe
                observacion = "Resultados de las acciones:\n" + "\n".join(resultados_para_ia) + "\n\nSi necesitas continuar ejecutando acciones, responde ÚNICAMENTE con el siguiente JSON. Si ya terminaste o no hay más acciones, responde en texto natural explicando lo que se hizo (sin JSON)."
                messages.append({"role": "user", "content": observacion})
                continue # Pasa a la siguiente iteración
                
        except Exception as e:
            print(f"Error procesando la respuesta JSON de la IA: {e}")

        # Guardar en base de datos la interaccion
        interaccion_id = None
        try:
            interaccion = InteraccionIA.objects.create(
                usuario_prompt=user_prompt,
                contexto=contexto_rag,
                respuesta_ia=respuesta_ia,
                acciones_ejecutadas=json.dumps(acciones_a_ejecutar) if 'acciones_a_ejecutar' in locals() and acciones_a_ejecutar else "",
                exitosa=True
            )
            interaccion_id = interaccion.id
        except Exception as e:
            print(f"No se pudo guardar la interaccion: {e}")

        # Si no es ninguna de las acciones o el flujo terminó, es una respuesta normal
        print("\n[Asistente Financiero]:")
        print(respuesta_ia)
        return {
            "respuesta": respuesta_ia,
            "id": interaccion_id,
        } # Salimos del ciclo y retornamos
    else:
        interaccion_id = None
        try:
            interaccion = InteraccionIA.objects.create(usuario_prompt=user_prompt, contexto=contexto_rag, respuesta_ia="Reached maximum iterations without final action.", exitosa=False)
            interaccion_id = interaccion.id
        except:
            pass
        return {"respuesta": "No se pudo concretar la acción final.", "id": interaccion_id}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Asistente financiero con IA")
    parser.add_argument("prompt", type=str, nargs="?", help="Instrucción para el asistente")
    args = parser.parse_args()

    if args.prompt:
        procesar_prompt_con_ia(args.prompt)
    else:
        print("Ejecutando en modo consola interactiva. Escribe 'salir' o 'exit' para terminar.\n")
        while True:
            user_input = input("Usuario: ")
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
            procesar_prompt_con_ia(user_input)
            print("-" * 40)
