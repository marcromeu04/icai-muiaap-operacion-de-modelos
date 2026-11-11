# 7.2 Nota: de gateway local a cliente HTTP

## Contrato de la API Wine

- URL: MODEL_API_URL + /v1/predictions
- Método: POST, con cabecera Accept: application/json y timeout de 5 s.
- Cuerpo: {"features": {las 11 características del vino}}
- Respuesta válida (2xx): {"prediction": {quality_band, confidence, model_version, preprocessing_version}, "request_id": ...}. Se valida con PredictionPayload antes de llegar al controlador.

## Traducción de fallos

| Fallo | Error de dominio | Qué ve la persona |
| --- | --- | --- |
| 422 | InputContractError | Datos no válidos; revisar el formulario |
| 503 o sin conexión | ArtifactUnavailableError | Modelo no disponible; reintentar más tarde |
| Timeout | InferenceTimeoutError | Tardó demasiado; reintentar |
| Otro status, JSON inválido o predicción incompatible | BackendInferenceError | No se pudo obtener la predicción |

Nunca se muestran el cuerpo de la respuesta, el traceback ni las features.

## Qué cambia respecto a S6

- Nuevo: HttpInferenceGateway (src/model_ui/http_gateway.py).
- app.py: 2 líneas en build_gateway. Si existe MODEL_API_URL, se usa el gateway HTTP.
- Sin cambios: formulario, PredictionController, estados, retry, clear, presentación y telemetría.

## Comprobaciones

- uv run python -m pytest -q: 34 passed.
- ruff check y ruff format --check: sin errores.
- App con MODEL_API_URL contra la API local: capturas de éxito y fallo traducido en semana7/capturas.
