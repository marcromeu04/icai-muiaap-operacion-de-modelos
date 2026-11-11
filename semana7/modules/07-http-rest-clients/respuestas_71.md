# 7.1 Respuestas

- GET /health: 200. POST válido: 200 (label maintenance_required). POST inválido: 422, campo rechazado measurements.vibration_mm_s ("must be a number"). Evidencia completa en evidencia_71.txt.
- ¿Por qué 422 y no 400? El JSON está bien escrito, pero no cumple el contrato: vibration_mm_s debe ser un número. Un 400 sería un JSON mal formado.
- ¿Por qué no se reintenta un POST a ciegas? Porque no es idempotente: si la primera petición llegó al servidor y solo se perdió la respuesta, repetirla podría registrar dos veces la misma predicción.
