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
from apiTransacciones.models.transaccion_model import Transaccion, TipoTransaccion, CategoriaTransaccion
from apiCuentas.models.cuenta_model import Cuenta
from apiBancos.models.banco_model import Banco
from apiPresupuestos.models.presupuesto_model import TransaccionProgramada

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
        
        # Obtener programadas
        programadas = TransaccionProgramada.objects.all().order_by('-id')[:10]
        historial_prog = "Transacciones Programadas:\n"
        for p in programadas:
            historial_prog += f"- {p.mes}/{p.anio} | Desc: {p.descripcion} | Monto: ${p.monto} | Estado: {p.estado}\n"

        return f"{resumen_cuentas}\n{historial}\n{historial_prog}"
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
        
        # Obtenemos o creamos un tipo por defecto (ej. EGRESO o INGRESO)
        tipo_accion = datos.get('tipo', 'EGRESO').upper()
        tipo, _ = TipoTransaccion.objects.get_or_create(accion=tipo_accion)

        # Categoria
        categoria_nombre = datos.get('categoria')
        categoria = None
        if categoria_nombre:
            categoria, _ = CategoriaTransaccion.objects.get_or_create(nombre=categoria_nombre.title())

        transaccion = Transaccion.objects.create(
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto=datos['monto'],
            descripcion=datos['descripcion'],
            tipo=tipo,
            categoria=categoria
        )
        return {"status": "success", "message": f"Transacción de ${transaccion.monto} creada para '{transaccion.descripcion}' exitosamente."}
    except Exception as e:
        return {"status": "error", "message": f"Error al crear transacción: {str(e)}"}

def crear_transaccion_programada(datos):
    """Crea una transacción programada en la base de datos para presupuestos."""
    try:
        cuenta = Cuenta.objects.get(id=datos.get('cuenta_id', 1))
        
        tipo_accion = datos.get('tipo', 'EGRESO').upper()
        tipo, _ = TipoTransaccion.objects.get_or_create(accion=tipo_accion)
        
        # Categoria
        categoria_nombre = datos.get('categoria')
        categoria = None
        if categoria_nombre:
            categoria, _ = CategoriaTransaccion.objects.get_or_create(nombre=categoria_nombre.title())
        
        actual = datetime.now()
        anio = datos.get('anio', actual.year)
        mes = datos.get('mes', actual.month)
        tipo_periodo = datos.get('tipo_periodo', 'MES')

        programada = TransaccionProgramada.objects.create(
            cuenta=cuenta,
            monto=datos['monto'],
            descripcion=datos['descripcion'],
            tipo=tipo,
            categoria=categoria,
            tipo_periodo=tipo_periodo,
            anio=anio,
            mes=mes,
            estado='PROGRAMADA'
        )
        return {"status": "success", "message": f"Transacción programada de ${programada.monto} para '{programada.descripcion}' registrada en {mes}/{anio}."}
    except Exception as e:
        return {"status": "error", "message": f"Error al programar transacción: {str(e)}"}

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

ENDPOINTS DISPONIBLES Y ESTRUCTURAS ESPERADAS:

1. "/api/bancos/": 
   - GET: Filtra bancos por nombre. Ej: {{"nombre": "Caja Social"}}. Devuelve lista de bancos con su "id" y "nombre".
   - POST: Crea un banco. Payload: {{"nombre": "string"}}

2. "/api/categorias-transaccion/":
   - GET: Lista las categorías existentes para obtener su "id".
   - POST: Crea una categoría. Payload: {{"nombre": "string", "descripcion": "string"}}

3. "/api/cuentas/": 
   - GET: Filtra cuentas. Parámetros permitidos: "nombre" (texto) o "banco" (ID numérico del banco obtenido de /api/bancos/).
   - POST: Crea una cuenta. Payload: {{"banco": 1, "saldo": 1000.0, "numero": 1234, "nombre": "Opcional"}} -> IMPORTANTE: "banco" DEBE SER EL ID NUMÉRICO.
   - PUT/PATCH a "/api/cuentas/{id}/": Modifica una transacción existente.
   - DELETE a "/api/cuentas/{id}/": Elimina una transacción.

4. "/api/tipos-transaccion/":
   - GET: Lista los tipos de transacción (ej. INGRESO, EGRESO, TRANSFERENCIA, etc.) para que obtengas su ID numérico.

5. "/api/transacciones/":
   - GET: Lista las transacciones.
   - POST: Crea una transacción. Payload: {{
        "monto": 150.0, 
        "descripcion": "string", 
        "tipo": 1, // ID numérico de TipoTransaccion
        "categoria": 2, // ID numérico de CategoriaTransaccion (opcional)
        "cuenta_origen": 1, // ID numérico de Cuenta (opcional)
        "cuenta_destino": 2 // ID numérico de Cuenta (opcional)
     }}
   - PUT/PATCH a "/api/transacciones/{id}/": Modifica una transacción existente.
   - DELETE a "/api/transacciones/{id}/": Elimina una transacción.

6. "/api/presupuestos/":
   - GET: Lista transacciones programadas o presupuestos. 
     Filtros permitidos: "tipo" (ID numérico), "categoria" (ID numérico), "mes" (número del 1 al 12), "estado" (ej. "PROGRAMADA", "EJECUTADA"), "transaccion_aplicada_isnull" (True/False). IMPORTANTE: Si necesitas listar y puedes usar estos filtros, úsalos pasando la clave requerida en el data del GET para mantener las respuestas lo más acotadas y pequeñas posibles.
   - POST: Crea una transacción programada. Payload: {{
        "monto": 100.0,
        "descripcion": "string",
        "tipo": 1, // ID numérico
        "categoria": 2, // ID numérico (opcional)
        "cuenta": 1, // ID numérico de la cuenta afectada
        "tipo_periodo": "MES",
        "anio": 2026,
        "mes": 3
     }}
   - POST a "/api/presupuestos/crear-repetitivas/": Crea transacciones programadas repetitivas por varios meses usando bulk_create. 
   Payload: {{
        "monto": 100.0,
        "descripcion": "string",
        "tipo": 1,
        "categoria": 2,
        "cuenta": 1,
        "tipo_periodo": "MES",   
        "anio": 2026,
        "mes_inicio": 4,
        "mes_fin": 12,
        "porcentaje": 10.0,
        "transaccion_base_descripcion": "Salario"
     }}
   - PATCH a "/api/presupuestos/{id}": Modifica una transacción programada.
   - PATCH a "/api/presupuestos/{id}/ejecutar/": Ejecuta una transacción programada.
   - DELETE a "/api/presupuestos/{id}/" borra una transacción programada (la cancela)

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
Además, REGLA IMPORTANTE DE EFICIENCIA: Siempre que vayas a realizar acciones de tipo GET, y consideres que es posible utilizar filtros (como mes, categoria, nombre, etc. según se te expuso antes), USALOS. El objetivo es mantener las peticiones y respuestas lo más pequeñas y precisas posibles.
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
        try:
            InteraccionIA.objects.create(
                usuario_prompt=user_prompt,
                contexto=contexto_rag,
                respuesta_ia=respuesta_ia,
                acciones_ejecutadas=json.dumps(acciones_a_ejecutar) if 'acciones_a_ejecutar' in locals() and acciones_a_ejecutar else "",
                exitosa=True
            )
        except Exception as e:
            print(f"No se pudo guardar la interaccion: {e}")

        # Si no es ninguna de las acciones o el flujo terminó, es una respuesta normal
        print("\n[Asistente Financiero]:")
        print(respuesta_ia)
        return {"respuesta": respuesta_ia} # Salimos del ciclo y retornamos
    else:
        try:
            InteraccionIA.objects.create(usuario_prompt=user_prompt, contexto=contexto_rag, respuesta_ia="Reached maximum iterations without final action.", exitosa=False)
        except:
            pass
        return {"respuesta": "No se pudo concretar la acción final."}

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
