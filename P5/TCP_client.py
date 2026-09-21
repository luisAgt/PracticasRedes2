import socket
import sys

SERVER_IP = "192.168.0.20"  # IP del Servidor Windows
SERVER_PORT = 7000
CLIENT_PORT = 4500  # Puerto origen indicado en la práctica


def enviar_segmento_tcp(identificador_segmento):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reutilizar el puerto local inmediatamente
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Fijar el puerto origen a 4500
        sock.bind(('', CLIENT_PORT))
        sock.connect((SERVER_IP, SERVER_PORT))

        mensaje = f"Segmento TCP {identificador_segmento}"
        sock.sendall(mensaje.encode('utf-8'))

        respuesta = sock.recv(1024)
        print(f"[{identificador_segmento}] Servidor respondió: {respuesta.decode('utf-8')}")
    except Exception as e:
        print(f"Error al enviar {identificador_segmento}: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        enviar_segmento_tcp(sys.argv[1])
    else:
        print("Uso: python3 cliente_tcp.py <T1|T2|T3|T4>")