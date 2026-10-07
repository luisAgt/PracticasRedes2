#!/usr/bin/env python3

import socket
import os
from datetime import datetime

HOST = "192.168.1.32"
PORT = 65432
buffer_size = 1024

# Crear la carpeta "archivos" si no existe aún
STORAGE_DIR = "archivos"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

with TCPServerSocket:
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen(5)
    print("El servidor TCP está disponible y en espera de solicitudes")

    Client_conn, Client_addr = TCPServerSocket.accept()

    with Client_conn:
        print("Cliente conectado desde:", Client_addr)

        while True:
            data = Client_conn.recv(buffer_size)

            if not data:
                break

            text = data.decode("utf-8").strip()

            # Finalizar sesión
            if text.upper() in ["SALIR", "ADIOS"]:
                print("Closing connection by Client.")
                break

            # Comando HOLA
            elif text.upper() == "HOLA":
                Client_conn.sendall(b"Hola Bienvenido al servidor TCP.")

            # Comando HORA
            elif text.upper() == "HORA":
                now = datetime.now().strftime("%H:%M:%S")
                Client_conn.sendall(f"Hora actual: {now}".encode("utf-8"))

            # Comando FECHA
            elif text.upper() == "FECHA":
                today = datetime.now().strftime("%Y-%m-%d")
                Client_conn.sendall(f"Fecha actual: {today}".encode("utf-8"))
                # Comando AYUDA
            elif text.upper() == "AYUDA":
                help_text = (
                    "Comandos disponibles:\n"
                    "- HOLA: Saludo del servidor.\n"
                    "- HORA: Muestra la hora actual.\n"
                    "- FECHA: Muestra la fecha actual.\n"
                    "- LISTAR: Lista los archivos en el servidor.\n"
                    "- CARGAR <ruta>: Sube un archivo al servidor.\n"
                    "- DESCARGAR <archivo>: Descarga un archivo del servidor.\n"
                    "- ADIOS / SALIR: Cierra la conexion."
                )
                Client_conn.sendall(help_text.encode("utf-8"))
            # Comando LISTAR
            elif text.upper() == "LISTAR":
                files = os.listdir(STORAGE_DIR)
                if files:
                    file_list = "\n".join(files)
                    Client_conn.sendall(f"Archivos en servidor:\n{file_list}".encode("utf-8"))
                else:
                    Client_conn.sendall(b"La carpeta 'archivos' esta vacia.")

            # Comando CARGAR (Recepción de archivo enviado por el cliente)
            elif text.startswith("FILE:"):
                # Formato esperado: FILE:nombre|SIZE:bytes
                header = text[5:]  # Quita "FILE:"
                name, size_str = header.split("|SIZE:")
                name = name.strip()
                size = int(size_str.strip())

                print(f"Recibiendo archivo: {name} ({size} bytes)")
                Client_conn.sendall(b"READY")

                save_path = os.path.join(STORAGE_DIR, name)

                with open(save_path, "wb") as file:
                    bytes_received = 0
                    while bytes_received < size:
                        datas = Client_conn.recv(buffer_size)
                        if not datas:
                            break
                        file.write(datas)
                        bytes_received += len(datas)

                print(f"Archivo {name} guardado con exito en {STORAGE_DIR}/.")
                Client_conn.sendall(b"TRANSFERENCE_COMPLETE")

            # Comando DESCARGAR (Envío de archivo hacia el cliente)
            elif text.upper().startswith("DESCARGAR"):
                # Acepta tanto "DESCARGAR archivo.txt" como "DESCARGAR:archivo.txt"
                if ":" in text:
                    filename = text.split(":", 1)[1].strip()
                else:
                    filename = text[9:].strip()

                file_path = os.path.join(STORAGE_DIR, filename)

                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)

                    # Notificar al cliente que el archivo existe y su tamaño
                    Client_conn.sendall(f"FILE:{filename}|SIZE:{size}".encode("utf-8"))

                    # Esperar confirmación READY del cliente
                    ack = Client_conn.recv(buffer_size)
                    if ack.decode("utf-8").strip() == "READY":
                        print(f"Enviando archivo {filename} al cliente...")
                        with open(file_path, "rb") as file:
                            while True:
                                datas = file.read(buffer_size)
                                if not datas:
                                    break
                                Client_conn.sendall(datas)
                        print(f"Archivo {filename} enviado correctamente.")
                else:
                    Client_conn.sendall(b"ERROR: El archivo solicitado no existe en la carpeta 'archivos/'.")

            else:
                Client_conn.sendall(b"Comando not found.")

        print("Conexion cerrada con el cliente.")

    print("Servidor finalizado.")