#!/usr/bin python3

import socket

HOST = "192.168.1.22"  # Hostname o  dirección IP del servidor
PORT = 65432  # Puerto del servidor
buffer_size = 1024

TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        print("Conectado correctamente")
        while True:
            text = input("Ingrese un mensaje: ")
            TCPClientSocket.sendall(text.encode())
            print("Esperando una respuesta...")
            data = TCPClientSocket.recv(buffer_size)
            print("Recibido,", repr(data), " de", TCPClientSocket.getpeername())

            if text.strip() == "goodbye":
                print("Ok, I'm closing the session...")
                break
finally:
    TCPClientSocket.close()