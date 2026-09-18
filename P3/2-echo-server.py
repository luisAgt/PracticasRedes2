#!/usr/bin python3wtt
import socket

from socketserver import TCPServer

HOST = "192.168.1.26"  # Direccion de la interfaz de loopback estándar (localhost)
PORT = 65432  # Puerto que usa el cliente  (los puertos sin provilegios son > 1023)
buffer_size = 1024
# TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# try:
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen(5)
    print("El servidor TCP está disponible y en espera de solicitudes")

    Client_conn, Client_addr = TCPServerSocket.accept()
    # Crear objeto thread (client_conn)
    # client_ip, client_port = Client_addr[0], Client_addr[1]
    # try:
    with Client_conn:
        print("Conectado a", Client_addr)
        while True:
            print("Esperando a recibir datos... ")
            data = Client_conn.recv(buffer_size)

            if not data:
                break

            text = data.decode("utf-8")
            print("Recibido,", data, "   de ", Client_addr)

            if text.startswith("FILE:"):
                header = text.replace("FILE:", "")
                name, size = header.split("|SIZE:")
                size = int(size)

                print("Getting the file ", name)
                print("size: ", size, "bytes")

                Client_conn.sendall(b"READY")
                with open("recibido_" + name, "wb") as file:
                    bytes_received = 0
                    while bytes_received < size:
                        datas = Client_conn.recv(buffer_size)

                        if not datas:
                            break

                        file.write(datas)
                        bytes_received += len(datas)
                        print(f"Bytes received:{bytes_received}" )
                print("File correctly received...\n")
                Client_conn.sendall(b"TRANSFERENCE_COMPLETE")
                print(f"Total received: {bytes_received} bytes")
                break
            # if text.strip().lower() == "goodbye":
            # print("Ok. I'm saying goodbye...")
            # Client_conn.sendall(text.encode("utf-8"))
            # break
            # if not data:
            # break
            print("Enviando respuesta a", Client_addr)
            Client_conn.sendall(data)
        # finally:
        # Client_conn.close()
        print("Connection close with client")
    # finally:
    # TCPServerSocket.close()
    print("Off server")