#!/usr/bin python3

import socket
import os #library for managment files and paths, etc.

HOST = "192.168.1.26"  # Hostname o  dirección IP del servidor
PORT = 65432  # Puerto del servidor
buffer_size = 1024

#TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#try:
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))
        print("Conectado correctamente")
        #while True:
            #text = input("Ingrese un mensaje: ")
        select = ("Send a file txt")
        route = input ("Select the route of your file: ").strip()
        route = os.path.expanduser(route)
        if os.path.exists(route):
            filename = os.path.basename(route)
            size = os.path.getsize(route)

        #TCPClientSocket.sendall(text.encode())

            #Exercise 01
            print(f"\n\t Update Exercise 01.")
            print(f"File name: {filename}")
            print(f"File Size: {size} bytes")
            print(f"Sending file... ... ... ....\n")


            TCPClientSocket.sendall(f"FILE: {filename}|SIZE: {size}".encode())
            #print("Esperando una respuesta...")
            data = TCPClientSocket.recv(buffer_size)
            print("Recibido,", repr(data), " de", TCPClientSocket.getpeername())

            if data.decode("utf-8").strip() == "READY":

                #exercise 02
                print(f"\n\t Update Exercise 02.")
                bytes_sent = 0
                with open(route, "rb") as file:
                    while True:
                        datas = file.read(buffer_size)
                        if not datas:
                            break
                        TCPClientSocket.sendall(datas)

                        #exercise 02
                        bytes_sent += len(datas)
                        print(f"Bytes sent: {bytes_sent}")

                print("\nFile correctly sent. :) \n")
                print(f"Total sent: {bytes_sent} bytes")
                ack_final = TCPClientSocket.recv(buffer_size)
                print("Confirm Server: ", ack_final.decode("utf-8"))
        else:
            print("The route doesn't exist")
            #if text.strip() == "goodbye":
            #    print("Ok, I'm closing the session...")
            #    break
#finally:
#TCPClientSocket.close()