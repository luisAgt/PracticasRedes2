#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"  # Escucha en todas las interfaces disponibles de la máquina
PORT_NAVEGADOR = 5000
PORT_CHAT = 6000

# Socket 1: Navegador (Puerto 5000)
s_navegador = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_navegador.bind((HOST, PORT_NAVEGADOR))
s_navegador.setblocking(False)  # Modo no bloqueante para revisar ambos sockets

# Socket 2: Chat (Puerto 6000)
s_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_chat.bind((HOST, PORT_CHAT))
s_chat.setblocking(False)

print("Servidor listo escuchando en puertos 5000 y 6000...")

while True:
    # Revisar puerto 5000 (Navegador)
    try:
        data, addr = s_navegador.recvfrom(1024)
        print(f"[NAVEGADOR - Puerto 5000] Recibido de {addr}: {data.decode()}")
    except BlockingIOError:
        pass

    # Revisar puerto 6000 (Chat)
    try:
        data, addr = s_chat.recvfrom(1024)
        print(f"[CHAT - Puerto 6000] Recibido de {addr}: {data.decode()}")
    except BlockingIOError:
        pass
