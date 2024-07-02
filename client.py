import socket
import json

# Definir el puerto y la dirección del servidor al que se va a conectar el cliente
HOST = '127.0.0.1'
PORT = 8080

def get_user_input():
    protocol_type = input("Ingrese el tipo de protocolo ('testing' o 'normal'): ").strip()

    if protocol_type == 'testing':
        nodos = input("Ingrese los nodos separados por coma (por ejemplo: 1030,1230,1150): ").strip().split(',')
        nodos = [int(nodo) for nodo in nodos]
        protocol = {
            "command": "testing",
            "nodos": nodos
        }

    elif protocol_type == 'normal':
        nodos = []
        num_nodos = int(input("Ingrese el número de nodos: ").strip())

        for _ in range(num_nodos):
            nodo = int(input("Ingrese el ID del nodo: ").strip())
            rpm1 = int(input("Ingrese RPM1: ").strip())
            rpm2 = int(input("Ingrese RPM2: ").strip())
            rpm3 = int(input("Ingrese RPM3: ").strip())
            rpm4 = int(input("Ingrese RPM4: ").strip())
            nodos.append({
                "nodo": nodo,
                "rpm1": rpm1,
                "rpm2": rpm2,
                "rpm3": rpm3,
                "rpm4": rpm4,
            })

        protocol = {
            "command": "normal",
            "nodos": nodos
        }

    else:
        raise ValueError("Protocolo no reconocido")

    return protocol

def send_protocol(protocol):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(json.dumps(protocol).encode())
    response = client.recv(4096)
    print(f'Respuesta del servidor: {response.decode()}')
    client.close()

if __name__ == "__main__":
    protocol = get_user_input()
    send_protocol(protocol)
