import socket

HOST = "0.0.0.0"
PORT = 7000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
server_socket.setblocking(False)  # Modo no bloqueante

print(f"Servidor TCP escuchando en puerto {PORT}...")

conexiones_activas = []

try:
    while True:
        # 1. Intentar aceptar nuevas conexiones
        try:
            conn, addr = server_socket.accept()
            conn.setblocking(False)
            conexiones_activas.append((conn, addr))
            print(f"\n[NUEVA CONEXIÓN ABIERTA]")
            print(f" -> Cuádrupla: ({addr[0]}, {addr[1]}, IP_destino, {PORT})")
            print(f" -> Total conexiones activas: {len(conexiones_activas)}")
        except BlockingIOError:
            pass  # No hay conexiones nuevas en este instante

        # 2. Leer datos de todas las conexiones activas sin cerrarlas
        for conn, addr in conexiones_activas[:]:
            try:
                data = conn.recv(1024)
                if data:
                    print(f" -> Mensaje recibido de {addr}: {data.decode('utf-8')}")
                    conn.sendall(b"Respuesta del Servidor TCP: ACK")
                else:
                    # El cliente cerró la conexión
                    print(f"\n[CONEXIÓN CERRADA POR EL CLIENTE] {addr}")
                    conexiones_activas.remove((conn, addr))
                    conn.close()
            except BlockingIOError:
                pass  # No hay datos nuevos de esta conexión aún
            except ConnectionResetError:
                print(f"\n[CONEXIÓN PERDIDA] {addr}")
                conexiones_activas.remove((conn, addr))
                conn.close()

except KeyboardInterrupt:
    print("\nCerrando servidor...")
    server_socket.close()