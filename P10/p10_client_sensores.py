#!/usr/bin/env python3
import socket
import time
import random
import sys

# Configuración del servidor
HOST = "192.168.0.113"
PORT = 65432

# Permitir pasar el ID del sensor por argumento o usar uno por defecto
# Ejemplo de uso en terminal: python3 cliente_sensor.py temp01
sensor_id = sys.argv[1] if len(sys.argv) > 1 else "temp01"

print(f"Iniciando sensor [{sensor_id}]...")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((HOST, PORT))
        print(f"Conectado exitosamente al servidor de monitoreo en {HOST}:{PORT}")
        
        while True:
            # Simular la lectura de un sensor (ej. temperatura entre 20.0 y 30.0 °C)
            valor = round(random.uniform(20.0, 30.0), 2)
            
            # Construir el mensaje con el formato exacto requerido: id, valor
            mensaje = f"{sensor_id},{valor}"
            
            # Enviar los datos al servidor
            client_sock.sendall(mensaje.encode('utf-8'))
            print(f"Enviado al servidor: {mensaje}")
            
            # Esperar la confirmación opcional del servidor
            try:
                client_sock.settimeout(2.0)
                respuesta = client_sock.recv(1024)
            except socket.timeout:
                pass  # Si no hay respuesta inmediata, continúa el ciclo
            
            # Enviar datos periódicamente cada 3 segundos 
            # (Nota: Debe ser menor al INACTIVITY_TIMEOUT del servidor para que no te desconecte)
            time.sleep(3)
            
except KeyboardInterrupt:
    print(f"\nSensor {sensor_id} detenido por el usuario.")
except ConnectionRefusedError:
    print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}. Asegúrate de que esté encendido.")