#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
buffer_size = 1024

# Estructura compartida: {conn: nickname}
clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_conn=None):
    """Envía un mensaje formateado a todos los clientes conectados."""
    with clients_lock:
        for client_conn in clients:
            if client_conn != sender_conn:
                try:
                    client_conn.sendall(message)
                except Exception as e:
                    print(f"Error al enviar broadcast: {e}")

def handle_client(client_conn, client_addr):
    """Maneja la comunicación individual con cada cliente en un hilo independiente."""
    nickname = "Desconocido"
    identifier = f"{client_addr[0]}:{client_addr[1]}"
    try:
        # 1. Recibir el nickname al inicio
        nickname_data = client_conn.recv(buffer_size)
        if not nickname_data:
            client_conn.close()
            return
        
        nickname = nickname_data.decode("utf-8").strip()
        
        with clients_lock:
            clients[client_conn] = nickname
            
        print(f"Cliente conectado: {identifier} ({nickname})")
        
        # Notificar a los demás que un usuario se unió
        join_msg = f"[Servidor]: {nickname} se ha unido".encode("utf-8")
        broadcast(join_msg, sender_conn=client_conn)
        
        # 2. Bucle para recibir mensajes
        while True:
            data = client_conn.recv(buffer_size)
            if not data:
                break
            
            message = data.decode("utf-8").strip()
            
            # Opción para desconectar si el cliente envía salir/adios
            if message.lower() in ["salir", "adios"]:
                print(f"[{nickname} - {identifier}] solicitó desconexión.")
                break
            
            # Demultiplexación lógica en consola
            print(f"[{nickname} - {identifier}]: {message}")
            
            # Reenviar mensajes a los demás clientes
            formatted_msg = f"[{nickname}]: {message}".encode("utf-8")
            broadcast(formatted_msg, sender_conn=client_conn)
            
    except (ConnectionResetError, ConnectionAbortedError):
        pass
    finally:
        # 3. Manejo de desconexiones (limpieza)
        with clients_lock:
            if client_conn in clients:
                del clients[client_conn]
        
        print(f"Cliente desconectado: {identifier} ({nickname})")
        leave_msg = f"[Servidor]: {nickname} ha abandonado el chat".encode("utf-8")
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
            thread = threading.Thread(target=handle_client, args=(client_conn, client_addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()