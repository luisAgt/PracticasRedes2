#!/usr/bin/env python3
import socket
import threading
import sys

HOST = "0.0.0.0"
PORT = 5000
buffer_size = 1024

# Estructura compartida: {conn: {"nickname": str, "addr": tuple}}
clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_conn=None):
    """Envía un mensaje formateado a todos los clientes conectados."""
    with clients_lock:
        for client_conn in clients:
            if client_conn != sender_conn:
                try:
                    client_conn.sendall(message)
                except Exception:
                    pass

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
            clients[client_conn] = {"nickname": nickname, "addr": client_addr}
            
        print(f"\n[+] Cliente conectado: {identifier} ({nickname})")
        
        # Notificar a los demás que un usuario se unió
        join_msg = f"[Servidor]: {nickname} se ha unido".encode("utf-8")
        broadcast(join_msg, sender_conn=client_conn)
        
        # 2. Bucle para recibir mensajes del cliente
        while True:
            data = client_conn.recv(buffer_size)
            if not data:
                break
            
            message = data.decode("utf-8").strip()
            
            if message.lower() in ["salir", "adios"]:
                break
            
            # Demultiplexación lógica en consola
            print(f"[{nickname} - {identifier}]: {message}")
            
            # Reenviar mensajes a los demás clientes
            formatted_msg = f"[{nickname}]: {message}".encode("utf-8")
            broadcast(formatted_msg, sender_conn=client_conn)
            
    except (ConnectionResetError, ConnectionAbortedError):
        pass
    finally:
        # 3. Limpieza y desconexión
        with clients_lock:
            if client_conn in clients:
                del clients[client_conn]
        
        print(f"\n[-] Cliente desconectado: {identifier} ({nickname})")
        leave_msg = f"[Servidor]: {nickname} ha abandonado el chat".encode("utf-8")
        broadcast(leave_msg)
        try:
            client_conn.close()
        except:
            pass

def server_console():
    """Hilo dedicado a leer la consola del servidor para enviar comunicados o desconectar usuarios."""
    print("\n--- Consola del Servidor Activa ---")
    print("Comandos disponibles:")
    print("  Escribe cualquier texto para enviarlo como mensaje del servidor a todos.")
    print("  desconectar <nickname> -> Expulsa a un usuario del chat.\n")
    
    while True:
        try:
            command = input()
            if not command.strip():
                continue
            
            # Comando para desconectar a un cliente por su nickname
            if command.lower().startswith("desconectar "):
                target_nickname = command[12:].strip()
                target_conn = None
                
                with clients_lock:
                    for conn, info in clients.items():
                        if info["nickname"].lower() == target_nickname.lower():
                            target_conn = conn
                            break
                
                if target_conn:
                    # Enviar aviso al cliente antes de cerrarle el socket
                    try:
                        target_conn.sendall(b"[Servidor]: Has sido desconectado por el servidor.")
                    except:
                        pass
                    
                    target_conn.close() # Esto disparará el cierre en su respectivo hilo
                    print(f"[Servidor]: Servidor desconectó a {target_nickname}.")
                    broadcast(f"[Servidor]: {target_nickname} ha sido desconectado por el servidor.".encode("utf-8"))
                else:
                    print(f"[Servidor]: No se encontró al usuario '{target_nickname}'.")
            
            else:
                # Enviar mensaje general del servidor a todos los clientes
                server_msg = f"[Servidor]: {command}".encode("utf-8")
                print(f"[Servidor (broadcast)]: {command}")
                broadcast(server_msg)
                
        except EOFError:
            break

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Servidor de chat iniciado y escuchando en el puerto {PORT}...")
    
    # Iniciar el hilo de la consola del servidor
    console_thread = threading.Thread(target=server_console)
    console_thread.daemon = True
    console_thread.start()
    
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