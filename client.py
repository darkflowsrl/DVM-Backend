import socket
import json

def enviar_json(data):
    HOST = '127.0.0.1'  # La dirección IP del servidor, en este caso localhost
    PORT = 8080        # El puerto en el que el servidor está escuchando
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        json_data = json.dumps(data)  # Convertir el diccionario en formato JSON
        s.sendall(json_data.encode())  # Enviar los datos codificados al servidor
        data = s.recv(1024)  # Esperar la respuesta del servidor
        print('Respuesta recibida:', data.decode())
        
        
testing: dict = {
    "command": "testing",
    "nodos": range(1, 2000)
}

normal: dict = {
    "command": "normal",
    "nodo": 1,
    "rpm1": 100,
    "rpm2": 200,
    "rpm3": 150,
    "rpm4": 180
}

configuracion_inicial: dict = {
    "command": "setConfiguracion",
    "configuraciones": [
        {
            "nodo": 1,
            "variacionRPM": 0.5,
            "subcorriente": 0.8,
            "sobrecorriente": 1.2,
            "cortocicuito": 1.5,
            "sensor": True,
            "electrovalvula": False
        },
        {
            "nodo": 2,
            "variacionRPM": 0.6,
            "subcorriente": 0.7,
            "sobrecorriente": 1.0,
            "cortocicuito": 1.3,
            "sensor": True,
            "electrovalvula": True
        },
        
        {
            "nodo": 1000,
            "variacionRPM": 0.6,
            "subcorriente": 0.7,
            "sobrecorriente": 1.0,
            "cortocicuito": 1.3,
            "sensor": True,
            "electrovalvula": True
        }
    ]
}

escanear: dict = {
    "command": "scan"
}

renombrar_nodo: dict = {
    "command": "renombrar",
    "nodo": 1,
    "nodoNombreNuevo": 5
}


if __name__ == "__main__":
    while True:
        print("Menu:")
        print("1. Enviar comando de prueba")
        print("2. Enviar comando de funcionamiento normal")
        print("3. Enviar comando de configuración inicial")
        print("4. Enviar comando de escaneo")
        print("5. Enviar comando de renombrar nodo")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            enviar_json(testing)
        elif opcion == "2":
            normal["nodo"] = int(input("Ingrese el número de nodo: "))
            enviar_json(normal)
        elif opcion == "3":
            enviar_json(configuracion_inicial)
        elif opcion == "4":
            enviar_json(escanear)
        elif opcion == "5":
            renombrar_nodo["nodo"] = int(input("Ingrese el número de nodo: "))
            renombrar_nodo["nodoNombreNuevo"] = int(input("Ingrese el nuevo nombre del nodo: "))
            enviar_json(renombrar_nodo)
        elif opcion == "6":
            break
        else:
            print("Opción inválida. Intente de nuevo.")
            
