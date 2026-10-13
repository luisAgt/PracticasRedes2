#!/usr/bin/env python3
import sys
import socket
import selectors
import types
import time

# Configuración del servidor
HOST = "localhost"
PORT = 65432
INACTIVITY_TIMEOUT = 15.0  # Segundos sin enviar datos antes de considerarlo inactivo

sel = selectors.DefaultSelector()
active_sensors_count = 0

def accept_wrapper(sock):
    global active_sensors_count
    sock_conn, addr = sock.accept()
    sock_conn.setblocking(False)
    
    # Estructura para almacenar el estado del sensor
    data = types.SimpleNamespace(
        addr=addr, 
        sensor_id=None, 
        last_active=time.time()
    )
    
    sel.register(sock_conn, selectors.EVENT_READ, data=data)
    active_sensors_count += 1
    
    print(f"\n[+] Conectado a {addr}")
    print(f"📊 Número de sensores activos: {active_sensors_count}")

def service_connection(key, mask):
    global active_sensors_count
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                # Actualizar tiempo de última actividad
                data.last_active = time.time()
                mensaje = recv_data.decode('utf-8').strip()
                
                # Procesar formato: sensor_id, valor (ej. temp01,23.5)[cite: 1]
                if "," in mensaje:
                    parts = mensaje.split(",", 1)
                    data.sensor_id = parts[0].strip()
                    valor = parts[1].strip()
                    print(f"Sensor {data.sensor_id} reporta: {valor}")[cite: 1]
                else:
                    print(f"Recibido de {data.addr}: {mensaje}")
                
                # Opcional: Responder al sensor confirmando recepción
                sock.sendall(b"OK")
            else:
                # Desconexión limpia iniciada por el cliente
                close_connection(sock, data, motivo="Desconectado por el cliente")
        except ConnectionResetError:
            close_connection(sock, data, motivo="Conexión reiniciada forzosamente")

def close_connection(sock, data, motivo="Timeout / Inactividad"):
    global active_sensors_count
    print(f"\n[-] {motivo} - Sensor ID: {data.sensor_id or 'Desconocido'} ({data.addr})")
    sel.unregister(sock)
    sock.close()
    active_sensors_count = max(0, active_sensors_count - 1)
    print(f"📊 Número de sensores activos: {active_sensors_count}")[cite: 2]

def check_timeouts():
    """Revisa si algún sensor ha superado el tiempo límite de inactividad."""
    current_time = time.time()
    for key in list(sel.get_map().values()):
        data = key.data
        if data is not None:  # Ignorar el socket principal del servidor
            if current_time - data.last_active > INACTIVITY_TIMEOUT:
                close_connection(key.fileobj, data, motivo="Timeout de inactividad alcanzado")

# --- Configuración Inicial del Socket Servidor ---
sock_accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_accept.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_accept.bind((HOST, PORT))
sock_accept.listen()
sock_accept.setblocking(False)

# Registrar el socket servidor en el selector
sel.register(sock_accept, selectors.EVENT_READ, data=None)

print(f"Servidor de sensores TCP iniciado en {HOST}:{PORT}")
print(f"Esperando conexiones de sensores... (Timeout de inactividad: {INACTIVITY_TIMEOUT}s)")

try:
    while True:
        # Timeout de 1 segundo para permitir la revisión periódica de inactividad
        events = sel.select(timeout=1.0)
        
        for key, mask in events:
            if key.data is None:
                # Evento en el socket servidor -> Nueva conexión
                accept_wrapper(key.fileobj)
            else:
                # Evento en un socket de cliente -> Datos recibidos
                service_connection(key, mask)
                
        # Verificar sensores inactivos en cada ciclo del bucle
        check_timeouts()
        
except KeyboardInterrupt:
    print("\nServidor detenido manualmente.")
finally:
    sel.close()