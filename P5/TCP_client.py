import socket
import sys

SERVER_IP = "192.168.0.20"  # Cambia por la IP de tu servidor
SERVER_PORT = 7000
CLIENT_PORT = 4500  # Puerto origen de la práctica


def mantener_conexion_tcp(identificador_segmento):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(('', CLIENT_PORT))
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"[{identificador_segmento}] Conexión establecida desde puerto local {CLIENT_PORT}.")

        # Enviar primer mensaje automático de identificación
        mensaje_inicial = f"Segmento TCP {identificador_segmento}"
        sock.sendall(mensaje_inicial.encode('utf-8'))

        respuesta = sock.recv(1024)
        print(f"[{identificador_segmento}] Servidor respondió: {respuesta.decode('utf-8')}")
        print("\n--- Conexión ABIERTA y ACTIVA ---")
        print("Escribe un mensaje para enviar sobre esta MISMA conexión (o Ctrl+C para salir):")

        # Bucle interactivo para MANTENER viva la conexión
        while True:
            texto = input(f"[{identificador_segmento}] > ")
            if texto.strip():
                sock.sendall(texto.encode('utf-8'))
                resp = sock.recv(1024)
                print(f"Servidor: {resp.decode('utf-8')}")

    except KeyboardInterrupt:
        print(f"\n[{identificador_segmento}] Finalizando y cerrando socket...")
    except Exception as e:
        print(f"[{identificador_segmento}] Error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mantener_conexion_tcp(sys.argv[1])
    else:
        print("Uso: python3 TCP_client.py <T1|T2|T3|T4>")