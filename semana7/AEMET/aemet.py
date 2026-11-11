"""Práctica AEMET: climatología diaria de octubre de 2019 en Madrid, Ciudad Universitaria."""

import os

import requests

BASE_URL = "https://opendata.aemet.es/opendata/api"
API_KEY = os.environ["AEMET_API_KEY"]


def get_data(url):
    """La AEMET responde en dos pasos: primero un JSON con el enlace "datos"."""
    response = requests.get(url, params={"api_key": API_KEY}, timeout=30)
    print("Status:", response.status_code)
    response.raise_for_status()
    first = response.json()
    print("Respuesta AEMET:", first["estado"], first["descripcion"])

    data_response = requests.get(first["datos"], timeout=30)
    data_response.raise_for_status()
    return data_response.json()


# 1. Inventario de estaciones: buscamos el indicativo (idema)
inventory_url = BASE_URL + "/valores/climatologicos/inventarioestaciones/todasestaciones"
stations = get_data(inventory_url)

idema = None
for station in stations:
    if station["nombre"] == "MADRID, CIUDAD UNIVERSITARIA":
        idema = station["indicativo"]
print("Indicativo de MADRID, CIUDAD UNIVERSITARIA:", idema)

# 2. Climatología diaria de octubre de 2019 para esa estación
start = "2019-10-01T00:00:00UTC"
end = "2019-10-30T23:59:59UTC"
daily_url = (
    BASE_URL
    + "/valores/climatologicos/diarios/datos"
    + f"/fechaini/{start}/fechafin/{end}/estacion/{idema}"
)
days = get_data(daily_url)

print("Días recibidos:", len(days))
for day in days:
    print(day["fecha"], "tmed:", day.get("tmed"), "prec:", day.get("prec"))
