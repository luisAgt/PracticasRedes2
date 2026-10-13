#!/usr/bin python3

import socket
import os #library for managment files and paths, etc.

HOST = "192.168.1.15"  # Hostname o  dirección IP del servidor
PORT = 65432  # Puerto del servidor
buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        print("Conectado correctamente. Write the correct comands to interact Server...")
        while True:
            message = input ("Enter a command: ").strip()

            if not message:
                continue
            cmd_lower = message.lower()
            #if message.lower() == "hola":
                #TCPClientSocket.sendall(message.encode("utf-8"))
                #print("Sending a greating")
                #continue

            #if message.lower() == "hora":
             #   TCPClientSocket.sendall(message.encode("utf-8"))
              #  print("Sending an hour")
               # continue

            #if message.lower() == "fecha":
             #   TCPClientSocket.sendall(message.encode("utf-8"))
              #  print("Sending a date")
               # continue

            if cmd_lower in  ["adios", "salir"]:
                TCPClientSocket.sendall(b"QUIET")
                print("Ending connection")
                break
            elif cmd_lower in ["hola", "hora", "fecha", "listar", "ayuda"]:
                TCPClientSocket.sendall(message.encode("utf-8"))
                print(f"Sending command: {message}")
                data = TCPClientSocket.recv(buffer_size)
                print("Server response:\n", data.decode("utf-8"))

            elif cmd_lower.startswith("cargar"):

                route = message[6:].strip()

                route = os.path.expanduser(route)

                if os.path.exists(route):

                    filename = os.path.basename(route)

                    size = os.path.getsize(route)

                    print(f"\nFile name: {filename}")

                    print(f"File Size: {size} bytes")

                    print(f"Sending file... ... ... ....\n")

                    # ENCABEZADO CORREGIDO (sin espacio tras FILE:)

                    TCPClientSocket.sendall(f"FILE:{filename}|SIZE:{size}".encode("utf-8"))

                    data = TCPClientSocket.recv(buffer_size)

                    if data.decode("utf-8").strip() == "READY":

                        bytes_sent = 0

                        with open(route, "rb") as file:

                            while True:

                                datas = file.read(buffer_size)

                                if not datas:
                                    break

                                TCPClientSocket.sendall(datas)

                                bytes_sent += len(datas)

                                print(f"Bytes sent: {bytes_sent}")

                        print("\nFile correctly sent. :) \n")

                        print(f"Total sent: {bytes_sent} bytes")

                        ack_final = TCPClientSocket.recv(buffer_size)

                        print("Confirm Server: ", ack_final.decode("utf-8"))

                        continue

                else:

                    print("The route doesn't exist")
            elif cmd_lower.startswith("descargar"):
                filename = message[10:].strip()

                if not filename:
                    print("You need especified the filename. Ej: DESCARGAR file1.txt")
                    continue

                TCPClientSocket.sendall(f"DESCARGAR:{filename}".encode("utf-8"))
                data = TCPClientSocket.recv(buffer_size)
                text_response = data.decode("utf-8").strip()

                # Si el servidor responde con el encabezado de transferencia
                if text_response.startswith("FILE:"):
                    header = text_response.replace("FILE:", "")
                    name, size = header.split("|SIZE:")
                    size = int(size)

                    print(f"\nDescargando archivo: {name} ({size} bytes)...")

                    # Confirmar al servidor que estamos listos para recibir
                    TCPClientSocket.sendall(b"READY")

                    save_name = "descargado_" + name
                    bytes_received = 0

                    with open(save_name, "wb") as file:
                        while bytes_received < size:
                            datas = TCPClientSocket.recv(buffer_size)
                            if not datas:
                                break
                            file.write(datas)
                            bytes_received += len(datas)
                            print(f"Bytes recibidos: {bytes_received}")

                    print(f"\nFile saved by '{save_name}'.")
                    print(f"Total received: {bytes_received} bytes")
                else:
                    # Muestra el error enviado por el servidor (ej. archivo no encontrado)
                    print("Server response:", text_response)

            else:
                print("Invalid command")

