#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
buffer_size = 1024

# Estructura compartida para almacenar los clientes conectados: {conn: nickname}
clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_conn=None):
    """Envía un mensaje a todos los clientes conectados excepto al que lo envió."""
    with clients_lock:
        for client_conn in clients:
            if client_conn != sender_conn:
                try:
                    client_conn.sendall(message)
                except:
                    pass

def handle_client(client_conn, client_addr):
    """Maneja la comunicación individual con cada cliente en un hilo independiente."""
    try:
        # 1. El cliente envía su nickname al inicio
        nickname_data = client_conn.recv(buffer_size)
        if not nickname_data:
            client_conn.close()
            return
        
        nickname = nickname_data.decode("utf-8").strip()
        identifier = f"{client_addr[0]}:{client_addr[1]}"
        
        with clients_lock:
            clients[client_conn] = nickname
            
        print(f"Cliente conectado: {identifier} ({nickname})")
        
        # Notificar a los demás que un usuario se unió
        join_msg = f"[Servidor]: {nickname} se ha unido\n".encode("utf-8")
        broadcast(join_msg, sender_conn=client_conn)
        
        # 2. Bucle para recibir y difundir mensajes del chat
        while True:
            data = client_conn.recv(buffer_size)
            if not data:
                break
            
            message = data.decode("utf-8").strip()
            
            # Demultiplexación lógica: Identificar quién envía el mensaje en consola
            print(f"[{nickname} - {identifier}]: {message}")
            
            # Formatear el mensaje para los demás: [Nickname]: Mensaje
            formatted_msg = f"[{nickname}]: {message}\n".encode("utf-8")
            broadcast(formatted_msg, sender_conn=client_conn)
            
    except (ConnectionResetError, ConnectionAbortedError):
        pass
    finally:
        # 3. Manejo de desconexiones
        with clients_lock:
            if client_conn in clients:
                nickname = clients[client_conn]
                del clients[client_conn]
        
        print(f"Cliente desconectado: {client_addr} ({nickname if 'nickname' in locals() else 'Desconocido'})")
        leave_msg = f"[Servidor]: {nickname if 'nickname' in locals() else 'Un usuario'} ha abandonado el chat\n".encode("utf-8")
        broadcast(leave_msg)
        client_conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Servidor escuchando en puerto {PORT}...")
    
    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            # Crear un nuevo thread para manejar ese cliente
            thread = threading.Thread(target=handle_client, args=(client_conn, client_addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()