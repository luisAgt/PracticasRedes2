#!/usr/bin/env python3
import socket
import threading
import sys

HOST = "192.168.0.113"  # IP de tu máquina virtual
PORT = 5000
buffer_size = 1024

def receive_messages(sock):
    """Hilo secundario para recibir continuamente los mensajes del servidor."""
    while True:
        try:
            data = sock.recv(buffer_size)
            if not data:
                print("\n[Servidor]: Conexión cerrada por el servidor.")
                break
            print(data.decode("utf-8"))
        except:
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}")
        sys.exit(1)
        
    print("Conectado al servidor")
    
    # Enviar el nickname al inicio
    nickname = input("Ingresa tu nombre: ").strip()
    if not nickname:
        nickname = "Anónimo"
    client_socket.sendall(nickname.encode("utf-8"))
    
    # Iniciar hilo receptor para escuchar mensajes de otros usuarios y del servidor
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.daemon = True
    recv_thread.start()
    
    # Bucle principal para enviar mensajes
    try:
        while True:
            message = input()
            if not message:
                continue
            
            client_socket.sendall(message.encode("utf-8"))
            
            if message.lower() in ["salir", "adios"]:
                print("Desconectando...")
                break
    except KeyboardInterrupt:
        print("\nSaliendo del chat...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()