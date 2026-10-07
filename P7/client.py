#!/usr/bin/env python3

import socket
import os

HOST = "192.168.1.22"
PORT = 65432
buffer_size = 1024

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        # Define un tiempo límite de 5 segundos para intentar conectar o recibir datos
        TCPClientSocket.settimeout(5.0)
        
        try:
            print(f"Intentando conectar a {HOST}:{PORT}...")
            TCPClientSocket.connect((HOST, PORT))
            # Quitamos el timeout para las operaciones normales de lectura del usuario
            TCPClientSocket.settimeout(None) 
            print("Conectado correctamente. Escribe 'ayuda' o 'help' para ver los comandos.")
            
            while True:
                message = input("\nEnter a command: ").strip()
                if not message:
                    continue

                cmd_lower = message.lower()

                if cmd_lower in ["adios", "salir", "exit", "quit", "bye"]:
                    TCPClientSocket.sendall(b"QUIET")
                    print("Ending connection")
                    break

                elif cmd_lower in ["hola", "hi", "hora", "time", "fecha", "date", "listar", "list", "ayuda", "help"] or cmd_lower.startswith("pedir ") or cmd_lower.startswith("order "):
                    TCPClientSocket.sendall(message.encode("utf-8"))
                    print(f"Sending request: {message}")
                    data = TCPClientSocket.recv(buffer_size)
                    if not data:
                        print("No response from server.")
                        continue
                    print("Server response:\n", data.decode("utf-8"))

                # (resto de tus bloques cargar/descargar se mantienen igual)

        except socket.timeout:
            print(f"\n[ERROR] Tiempo de espera agotado. No se pudo alcanzar la IP {HOST}.")
            print("Revisa si la VPN está activa, la IP es correcta o si el firewall de la MV está bloqueando el puerto.")
        except ConnectionRefusedError:
            print(f"\n[ERROR] Conexión rechazada por {HOST}:{PORT}.")
            print("La IP es alcanzable, pero el servidor.py no está en ejecución dentro de la MV o el puerto está cerrado.")
        except Exception as e:
            print(f"\n[ERROR] No se pudo conectar: {e}")

if __name__ == "__main__":
    main()