import requests
import urllib.parse

geocode_url = "http://localhost:8082/api/1/geocode?"
route_url = "http://localhost:8082/api/1/route?"
key = "6f16d4fc-4bb7-4741-9f8d-f8d7257ecb2f"

def geocoding(location, key):
    while location == "":
        location = input("Ingrese la ubicación nuevamente: ")
    # MEJORA 1 y 4: Idioma español mediante 'locale': 'es'
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key, "locale": "es"})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""

        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name

        print("URL de API Geocoding para " + new_loc + " (Tipo de ubicación: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status == 200:
            json_status = 404
            print("Ubicación no encontrada: " + location)
        else:
            print("Estado de API Geocoding: " + str(json_status) + "\nMensaje de error: " + json_data["message"])
    return json_status, lat, lng, new_loc

while True:
    # MEJORA 1 y 3: Entradas en español y salida con 's' o 'salir'
    loc1 = input("\nUbicación de Origen (o 's' / 'salir' para terminar): ")
    if loc1.lower() in ["s", "salir", "q", "quit"]:
        print("Programa finalizado.")
        break
    orig = geocoding(loc1, key)

    loc2 = input("Ubicación de Destino: ")
    if loc2.lower() in ["s", "salir", "q", "quit"]:
        print("Programa finalizado.")
        break
    dest = geocoding(loc2, key)

    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        # MEJORA 4: 'locale': 'es' para las instrucciones giro a giro en español
        paths_url = route_url + urllib.parse.urlencode({"key": key, "locale": "es"}) + op + dp
        paths_status = requests.get(paths_url).status_code
        paths_data = requests.get(paths_url).json()
        print("Estado de API Ruta: " + str(paths_status) + "\nURL de API Ruta:\n" + paths_url)

        print("=================================================")
        print("Indicaciones desde " + orig[3] + " hasta " + dest[3])
        print("=================================================")
        if paths_status == 200:
            km = (paths_data["paths"][0]["distance"]) / 1000
            meters = paths_data["paths"][0]["distance"]
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)

            # MEJORA 2: Formato a dos decimales (.2f)
            print("Distancia Recorrida: {0:.2f} km / {1:.2f} m".format(km, meters))
            print("Duración del Viaje: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")
            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                # MEJORA 2: Formato a dos decimales (.2f) en instrucciones
                print("{0} ( {1:.2f} km / {2:.2f} m )".format(path, distance / 1000, distance))
            print("=============================================")
        else:
            print("Mensaje de error: " + paths_data["message"])
            print("*************************************************")
            # Fin del programa