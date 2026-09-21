#!/usr/bin python3
import socket

SERVER_IP = "192.168.0.20"  # IP del Servidor Windows


def func_client(puerto_origen, puerto_destino, nombre_datagrama):
    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Se le asigna explícitamente el puerto de origen (4000, 4001, 4002)
    sock.bind(('', puerto_origen))

    # Enviar datagrama
    mensaje = f"Datagrama {nombre_datagrama} desde puerto {puerto_origen}"
    sock.sendto(mensaje.encode('utf-8'), (SERVER_IP, puerto_destino))
    print(f"Enviado {nombre_datagrama}: Origen {puerto_origen} -> Destino {puerto_destino}")

    sock.close()


# Envío de los datagramas según el pizarrón:
func_client(4000, 5000, "U1")  # S1 (4000) -> 5000
func_client(4001, 5000, "U2")  # S2 (4001) -> 5000
func_client(4002, 6000, "U3")  # S3 (4002) -> 6000