# 7.1 Respuestas

| Petición | Método y path | Content-Type | Status | request_id | Campo rechazado |
| --- | --- | --- | --- | --- | --- |
| Salud | GET /health | - | 200 | req_bd828f3f0b76 | - |
| Válida | POST /v1/predictions | application/json | 200 | req_762fda70d749 | - |
| Inválida | POST /v1/predictions | application/json | 422 | req_5e4ae781b1c1 | measurements.vibration_mm_s ("must be a number") |

La evidencia completa está en evidencia_71.txt.

- maintenance_required no es un error HTTP: es la predicción del modelo, y el status es 200.
- ¿Por qué 422 y no 400? El JSON está bien escrito, pero no cumple el contrato: vibration_mm_s debe ser un número. Un 400 sería un JSON mal formado.
- ¿Por qué no se reintenta un POST a ciegas? Porque no es idempotente: si la primera petición llegó al servidor y solo se perdió la respuesta, repetirla podría registrar dos veces la misma predicción.
