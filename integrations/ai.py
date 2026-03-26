import os
import sys
import json
import django
from datetime import datetime
from llama_cpp import Llama

import requests

# 1. Configurar Django para poder usar los modelos/endpoints desde el script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EFT.settings')
django.setup()

# Importar los modelos necesarios
from apiTransacciones.models.transaccion_model import Transaccion

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
            resumen_cuentas += f"- ID: {c.id} | Banco: {c.banco.nombre} | Saldo: ${c.saldo}\n"

        # Obtener transacciones
        transacciones = Transaccion.objects.all().order_by('-id')[:30]
        historial = "Últimas transacciones:\n"
        for t in transacciones:
            tipo_nombre = t.tipo.accion if t.tipo and t.tipo.accion else "N/A"
            origen = f"{t.cuenta_origen.id}" if t.cuenta_origen else "N/A"
            destino = f"{t.cuenta_destino.id}" if t.cuenta_destino else "N/A"
            historial += f"- {t.fecha.strftime('%Y-%m-%d')} | Desc: {t.descripcion} | Monto: ${t.monto} | Tipo: {tipo_nombre} | Origen: {origen} | Destino: {destino}\n"
        
        return f"{resumen_cuentas}\n{historial}"
    except Exception as e:
        return f"Error al obtener historial: {str(e)}"

def crear_cuenta(datos):
    """Crea un banco si no existe y luego una cuenta."""
    try:
        nombre_banco = datos.get('banco_nombre', 'Banco Desconocido')
        saldo = datos.get('saldo_inicial', 0.0)
        
        banco, created = Banco.objects.get_or_create(nombre=nombre_banco)
        cuenta = Cuenta.objects.create(banco=banco, saldo=saldo)
        
        return {"status": "success", "message": f"Cuenta ID {cuenta.id} creada en {banco.nombre} con saldo inicial de ${saldo}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear cuenta: {str(e)}"}

def crear_transaccion(datos):
    """Crea una transacción en la base de datos."""
    try:
        # Extraer orígenes y destinos (puede ser null)
        origen_id = datos.get('cuenta_origen_id')
        destino_id = datos.get('cuenta_destino_id')
        
        cuenta_origen = Cuenta.objects.get(id=origen_id) if origen_id else None
        cuenta_destino = Cuenta.objects.get(id=destino_id) if destino_id else None
        
        # Categoria
        categoria_nombre = datos.get('categoria')
        categoria = None
        tipo = None
        if categoria_nombre:
            categoria = CategoriaTransaccion.objects.filter(nombre__iexact=categoria_nombre).first()
            tipo = categoria.TipoTransaccion if categoria else None

        if not categoria or not tipo:
            return {
                "status": "error",
                "message": "Se requiere categoria con tipo configurado para crear transacciones."
            }

        transaccion = Transaccion.objects.create(
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto=datos['monto'],
            descripcion=datos['descripcion'],
            categoria=categoria
        )
        return {"status": "success", "message": f"Transacción de ${transaccion.monto} creada para '{transaccion.descripcion}' exitosamente."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear transacción: {str(e)}"}

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

def procesar_prompt_con_ia(user_prompt):
    model_path = "./llms/Qwen3.5-4B-Q8_0.gguf"
    
    if not os.path.exists(model_path):
        print(f"Error: No se encontró el modelo local en {model_path}.")
        return

    # Usar RAG (Generación Aumentada por Recuperación)
    contexto_rag = obtener_historial_transacciones()
    contexto_memoria = obtener_memoria_ia()

    print("Cargando el modelo...")
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=-1,
        seed=1337,
        n_ctx=10240,
        verbose=False # Desactivar verbosidad
    )

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

REGLA IMPORTANTE PARA TRANSACCIONES FUTURAS: Si el usuario indica que "debe realizar" un movimiento, "tiene una deuda", "tiene que hacer un pago", o se refiere a un gasto o ingreso en el futuro, ESTO NO ES UNA TRANSACCIÓN NORMAL. DEBES registrarlo como una Transacción Programada llamando al POST de "/api/presupuestos/". Utiliza el POST de "/api/transacciones/" ÚNICAMENTE para movimientos que ya ocurrieron o se efectúan en este preciso momento.

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

2. "/api/categorias-transaccion/"
    - POST esperado: {{"nombre": "string", "descripcion": "string"}}

3. "/api/tipos-transaccion/"
    - Usalo para resolver IDs de tipos (INGRESO, EGRESO, TRANSFERENCIA, etc.)

4. "/api/cuentas/"
    - Filtros recomendados en GET: "nombre", "banco"
    - POST esperado: {{"banco": 1, "saldo": 1000.0, "numero": 1234, "nombre": "Opcional"}}
    - IMPORTANTE: "banco" siempre es ID numerico

5. "/api/transacciones/"
    - POST esperado: {{
         "monto": 150.0,
         "descripcion": "string",
         "categoria": 2,
         "cuenta_origen": 1,
         "cuenta_destino": 2
      }}
    - IMPORTANTE: el tipo se infiere desde la categoria (categoria.TipoTransaccion)
    - Para hechos FUTUROS usa presupuestos, no transacciones directas

7. CATEGORIAS DE TRANSFERENCIA
        - Para transferencias entre cuentas usa categorias especiales:
            - "transferencia_egr" para salida
            - "transferencia_ing" para entrada
        - El sistema crea doble movimiento (egreso + ingreso) con acciones personalizadas.

6. "/api/presupuestos/"
    - Filtros disponibles en GET: "tipo" (derivado de categoria), "categoria", "mes", "descripcion", "estado", "transaccion_aplicada_isnull"
    - POST esperado: {{
         "monto": 100.0,
         "descripcion": "string",
         "categoria": 2,
         "cuenta": 1,
         "tipo_periodo": "MES",
         "anio": 2026,
         "mes": 3
      }}

C) ACCIONES PERSONALIZADAS (NO CRUD)
0. POST "/api/transacciones/transferencia/"
    - Registra una transferencia real entre cuentas como dos transacciones (egreso e ingreso)
    - Payload esperado: {{
         "monto": 150.0,
         "descripcion": "string",
         "cuenta_origen": 1,
         "cuenta_destino": 2
      }}

1. POST "/api/presupuestos/crear-repetitivas/"
    - Crea varias transacciones programadas por rango mensual
    - Payload esperado: {{
         "monto": 100.0,
         "descripcion": "string",
         "categoria": 2,
         "cuenta": 1,
         "tipo_periodo": "MES",
         "anio": 2026,
         "mes_inicio": 4,
         "mes_fin": 12,
         "porcentaje": 10.0, (opcional)
         "transaccion_base_descripcion": "Salario" (opcional)
      }}

2. POST "/api/presupuestos/con-interes/"
    - Planea transacciones programadas con interes para EGRESO (cuotas hasta agotar total) o INGRESO (rendimientos por periodos)
    - Payload esperado: {{
         "monto_base": 1000.0,
         "tasa_interes": 10.0,
         "numero_periodos": 6,
         "descripcion": "string",
         "categoria": 2,
         "cuenta": 1,
         "anio_inicio": 2026,
         "mes_inicio": 4,
         "tipo_periodo": "MES",
         "capitalizar": true
      }}

3. PATCH "/api/presupuestos/{id}/ejecutar/"
    - Ejecuta una transaccion programada y la marca como EJECUTADA

4. GET "/api/presupuestos/consolidado-mensual/"
        - Retorna consolidado mensual de presupuestos
        - Query params esperados: {{
                 "mes": 4,
                 "anio": 2026
            }}

        5. POST "/api/presupuestos/transferencia/"
            - Programa una transferencia futura entre cuentas como dos presupuestos (egreso e ingreso)
            - Payload esperado: {{
                 "monto": 150.0,
                 "descripcion": "string",
                 "cuenta_origen": 1,
                 "cuenta_destino": 2,
                 "tipo_periodo": "MES" (también es posible "SEMANA" o "DIA"), 
                 "anio": 2026,
                 "mes": 6,
                 "semana" : 0 (opcional),
                 "fecha_exacta": 24/04/2026 (opcional, usar cuando el periodo es tipo DIA)
              }}
        - Respuesta esperada: {{
                 "mes": 4,
                 "anio": 2026,
                 "total_gastos": "300.00",
                 "total_ingresos": "1000.00",
                 "excedente_mensual": "700.00"
            }}

Ejemplo de respuesta en un paso de tu ejecución:
{{
  "acciones": [
    {{
      "endpoint": "/api/categorias-transaccion/",
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
Además, REGLA IMPORTANTE DE EFICIENCIA: Siempre que vayas a realizar acciones de tipo GET, y consideres que es posible utilizar filtros (como mes, categoria, nombre, etc. según se te expuso antes), USALOS. Para consultas de presupuestos prioriza filtrar por "categoria" antes que por "descripcion" cuando la categoria sea deducible; si debes filtrar por "descripcion", usa UNA palabra clave en lugar de un texto largo. El objetivo es mantener las peticiones y respuestas lo más pequeñas y precisas posibles.
REGLA DE CONSULTA DE DOCUMENTACION: No llames "/api/schema/" en cada solicitud. Usalo solo cuando tengas duda real del contrato de un endpoint, y luego continúa con llamadas filtradas y específicas.
"""
    
    print(f"\n[Usuario]: {user_prompt}\n")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    MAX_ITERATIONS = 5
    for iteracion in range(MAX_ITERATIONS):
        output = llm.create_chat_completion(
            messages=messages,
            temperature=0.1,  
            repeat_penalty=1.1
        )

        respuesta_ia = output['choices'][0]['message']['content'].strip()
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
                    
                    url = f"http://127.0.0.1:8000{endpoint}"
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
