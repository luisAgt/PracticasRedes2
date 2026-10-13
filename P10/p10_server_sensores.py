#!/usr/bin/env python3
import socket
import selectors
import types
import time

HOST = "0.0.0.0"
PORT = 65432
INACTIVITY_TIMEOUT = 15.0

sel = selectors.DefaultSelector()
active_sensors_count = 0

def accept_wrapper(sock):
    global active_sensors_count
    sock_conn, addr = sock.accept()
    sock_conn.setblocking(False)
    
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
                data.last_active = time.time()
                mensaje = recv_data.decode('utf-8').strip()
                
                if "," in mensaje:
                    parts = mensaje.split(",", 1)
                    data.sensor_id = parts[0].strip()
                    valor = parts[1].strip()
                    print(f"Sensor {data.sensor_id} reporta: {valor}")
                else:
                    print(f"Recibido de {data.addr}: {mensaje}")
                
                sock.sendall(b"OK")
            else:
                close_connection(sock, data, motivo="Desconectado por el cliente")
        except (ConnectionResetError, ConnectionAbortedError):
            close_connection(sock, data, motivo="Conexión interrumpida")

def close_connection(sock, data, motivo="Inactividad"):
    global active_sensors_count
    print(f"\n[-] {motivo} - Sensor ID: {data.sensor_id or 'Desconocido'} ({data.addr})")
    sel.unregister(sock)
    sock.close()
    active_sensors_count = max(0, active_sensors_count - 1)
    print(f"📊 Número de sensores activos: {active_sensors_count}")

def check_timeouts():
    current_time = time.time()
    for key in list(sel.get_map().values()):
        data = key.data
        if data is not None:
            if current_time - data.last_active > INACTIVITY_TIMEOUT:
                close_connection(key.fileobj, data, motivo="Timeout de inactividad alcanzado")

sock_accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_accept.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_accept.bind((HOST, PORT))
sock_accept.listen()
sock_accept.setblocking(False)

sel.register(sock_accept, selectors.EVENT_READ, data=None)

print(f"Servidor de sensores TCP iniciado en {HOST}:{PORT}")
print(f"Esperando conexiones de sensores... (Timeout de inactividad: {INACTIVITY_TIMEOUT}s)")

try:
    while True:
        events = sel.select(timeout=1.0)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
        check_timeouts()
except KeyboardInterrupt:
    print("\nServidor detenido manualmente.")
finally:
    sel.close()