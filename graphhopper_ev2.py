import requests 
import urllib.parse 

# ==============================================================================
# 1. CONFIGURACIÓN DE LAS URLS DE LA API DE GRAPHHOPPER
# ==============================================================================
geocode_url = "https://graphhopper.com/api/1/geocode?" 
route_url   = "https://graphhopper.com/api/1/route?" 
key         = "a1c24a9b-a52e-4c7b-9d7c-6aac15bbf2e9"  # Tu API Key de Graphhopper

# Diccionario para traducir los perfiles ingresados por el usuario a los requeridos por la API
PERFILES_API = {
    "auto": "car",
    "bicicleta": "bike",
    "caminar": "foot"
}

# ==============================================================================
# 2. FUNCIÓN DE GEOCODIFICACIÓN (OBTENER COORDENADAS)
# ==============================================================================
def geocoding(location, key):
    # Re-solicitar la ubicación si el usuario presionó Enter vacío
    while location == "":
        location = input("Introduce la ubicación de nuevo: ").strip()
        
    # Añadimos locale=es para buscar preferentemente nombres en español si existen
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key, "locale": "es"})
    replydata   = requests.get(url) 
    json_data   = replydata.json() 
    json_status = replydata.status_code 

    # Verificar estado exitoso (200) y que la lista 'hits' no esté vacía
    if json_status == 200 and len(json_data["hits"]) != 0: 
        lat   = json_data["hits"][0]["point"]["lat"]
        lng   = json_data["hits"][0]["point"]["lng"]
        name  = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        
        # Extraer campos opcionales previniendo errores si no existen en el JSON
        country = json_data["hits"][0].get("country", "") 
        state   = json_data["hits"][0].get("state", "") 
        
        # Formatear el nombre completo de la locación
        if len(state) != 0 and len(country) != 0: 
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0: 
            new_loc = name + ", " + state 
        elif len(country) != 0:
            new_loc = name + ", " + country
        else: 
            new_loc = name
            
        print("URL de la API de Geocodificación para " + new_loc + " (Tipo de lugar: " + value + ")\n" + url)
        
    else: 
        # Valores por defecto en caso de fallo
        lat = lng = "null"
        new_loc = location
        
        # Reportar explícitamente problemas de credenciales o errores HTTP
        if json_status != 200:
            print("Estado de la API de Geocodificación: " + str(json_status))
            if "message" in json_data:
                print("Mensaje de error: " + json_data["message"])
        else:
            print("Estado de la API de Geocodificación: 200\nMensaje de error: Ubicación no encontrada.")

    return json_status, lat, lng, new_loc


# ==============================================================================
# 3. BUCLE PRINCIPAL INTERACTIVO (VERSIÓN FINAL DE LA APLICACIÓN)
# ==============================================================================
while True:
    print("\n" + "+" * 45)
    print("Perfiles de transporte disponibles en Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("auto, bicicleta, caminar")
    print("+" * 45)
    
    # Selección de vehículo y opción de salida
    entrada_vehiculo = input("Introduce un perfil de transporte de la lista anterior: ").strip().lower()
    if entrada_vehiculo in ["quit", "q", "salir"]:
        break
        
    # Validar el perfil en español y asignar el correspondiente para la API Graphhopper
    if entrada_vehiculo in PERFILES_API:
        vehicle = PERFILES_API[entrada_vehiculo]
    else:
        entrada_vehiculo = "auto"
        vehicle = "car"
        print("No se introdujo un perfil válido. Se usará el perfil por defecto: auto.")

    # --- ENTRADA Y RESOLUCIÓN DE ORIGEN ---
    loc1 = input("Ubicación de Origen: ").strip()
    if loc1.lower() in ["quit", "q", "salir", "kk", "ñ"]:
        break
    orig = geocoding(loc1, key)
    
    # Si la geocodificación falló, saltamos al inicio para no romper las rutas
    if orig[1] == "null":
        print("Ubicación de origen no válida. Por favor, inicia una nueva consulta.")
        continue

    # --- ENTRADA Y RESOLUCIÓN DE DESTINO ---
    loc2 = input("Ubicación de Destino: ").strip()
    if loc2.lower() in ["quit", "q", "salir", "kk", "ñ"]:
        break
    dest = geocoding(loc2, key)
    
    if dest[1] == "null":
        print("Ubicación de destino no válida. Por favor, inicia una nueva consulta.")
        continue

    # --- CÁLCULO DE LA RUTA (ROUTING API) ---
    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        # Formatear puntos de coordenadas para la URL
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        
        # Construir la URL agregando 'locale=es' para forzar las indicaciones paso a paso en español
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle, "locale": "es"}) + op + dp
        
        # Petición HTTP a la API de Rutas
        paths_response = requests.get(paths_url)
        paths_status   = paths_response.status_code
        paths_data     = paths_response.json()
        
        print("Estado de la API de Rutas: " + str(paths_status) + "\nURL de la API de Rutas:\n" + paths_url)
        
        # Procesar los datos de ruta si el estado es correcto
        if paths_status == 200:
            print("=================================================")
            print("Indicaciones desde " + orig[3] + " hasta " + dest[3] + " viajando en " + entrada_vehiculo)
            print("=================================================")
            
            # Calcular distancias (de metros a millas y kilómetros)
            distance_meters = paths_data["paths"][0]["distance"]
            miles = distance_meters / 1000 / 1.61
            km    = distance_meters / 1000
            
            # Calcular duración (de milisegundos a hh:mm:ss)
            time_ms = paths_data["paths"][0]["time"]
            sec = int((time_ms / 1000) % 60)
            min = int((time_ms / 1000 / 60) % 60)
            hr  = int(time_ms / 1000 / 60 / 60)
            
            print("Distancia Recorrida: {0:.1f} km / {1:.1f} millas".format(km, miles))
            print("Duración del Viaje: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")
            
            # --- IMPRESIÓN PASO A PASO (INSTRUCTIONS LOOP) ---
            instructions = paths_data["paths"][0]["instructions"]
            print("Instrucciones de navegación paso a paso:")
            for each in range(len(instructions)):
                path = instructions[each]["text"]
                dist = instructions[each]["distance"]
                print(" {0} ({1:.1f} km / {2:.1f} millas)".format(path, dist/1000, dist/1000/1.61))
            print("=================================================")
            
        else:
            # Captura de errores de cálculo de rutas
            if "message" in paths_data:
                print("Mensaje de error: " + paths_data["message"])
            print("*************************************************")