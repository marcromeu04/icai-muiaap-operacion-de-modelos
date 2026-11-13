import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
def definir_tool():
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": "Calcula la probabilidad de impago de una solicitud de prestamo.",
            "parameters": PrestamoEntrada.model_json_schema(),
        },
    }


# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
def ejecutar_tool(nombre, argumentos_json):
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": "Herramienta desconocida: " + str(nombre)}
    try:
        datos = json.loads(argumentos_json)
    except (json.JSONDecodeError, TypeError):
        return {"ok": False, "error": "Los argumentos no son un JSON valido."}
    try:
        entrada = PrestamoEntrada.model_validate(datos)
    except ValidationError as error:
        return {"ok": False, "error": str(error)}
    salida = predecir(entrada)
    return {"ok": True, **salida.model_dump()}


# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)
def responder(mensajes, llm):
    historial = [{"role": "system", "content": SISTEMA}]
    for m in mensajes:
        historial.append(m.model_dump())
    herramientas = [definir_tool()]
    herramienta = None

    for _ in range(MAX_VUELTAS):
        respuesta = llm.completar(historial, herramientas)
        llamadas = respuesta.get("tool_calls")
        if not llamadas:
            return ChatSalida(respuesta=respuesta.get("content") or "", herramienta=herramienta)

        historial.append(respuesta)
        for llamada in llamadas:
            nombre = llamada["function"]["name"]
            argumentos = llamada["function"]["arguments"]
            resultado = ejecutar_tool(nombre, argumentos)
            herramienta = HerramientaUsada(
                nombre=nombre, argumentos=leer_argumentos(argumentos), resultado=resultado
            )
            historial.append(
                {"role": "tool", "tool_call_id": llamada["id"], "content": json.dumps(resultado)}
            )

    return ChatSalida(
        respuesta="No he podido completar el calculo. Revisa los datos de la solicitud.",
        herramienta=herramienta,
    )
