import socket

HOST = "0.0.0.0"
PORT = 7000

# Crear socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server:
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((HOST, PORT))
    tcp_server.listen(5)
    print(f"Servidor de Archivos TCP escuchando en el puerto {PORT}...")

    while True:
        # accept() genera un nuevo socket dedicado exclusivamente a la cuádrupla del cliente
        conn, addr = tcp_server.accept()
        ip_origen, puerto_origen = addr

        print(f"\n[NUEVA CONEXIÓN ACEPTADA]")
        print(f" -> Cuádrupla: ({ip_origen}, {puerto_origen}, 192.168.0.20, {PORT})")

        with conn:
            data = conn.recv(1024)
            if data:
                print(f" -> Datos recibidos: {data.decode('utf-8')}")
                conn.sendall(b"Respuesta del Servidor TCP: ACK")