#!/usr/bin/env python3
import socket
import time
import random
import sys

HOST = "192.168.0.113"
PORT = 65432

sensor_id = sys.argv[1] if len(sys.argv) > 1 else "temp01"
print(f"Iniciando sensor [{sensor_id}]...")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((HOST, PORT))
        print(f"Conectado exitosamente al servidor en {HOST}:{PORT}")
        
        while True:
            valor = round(random.uniform(20.0, 30.0), 2)
            mensaje = f"{sensor_id},{valor}"
            
            try:
                client_sock.sendall(mensaje.encode('utf-8'))
                print(f"Enviado al servidor: {mensaje}")
            except BrokenPipeError:
                print("Error: El servidor cerró la conexión abruptamente.")
                break
                
            time.sleep(3)
            
except KeyboardInterrupt:
    print(f"\nSensor {sensor_id} detenido.")
except ConnectionRefusedError:
    print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}.")