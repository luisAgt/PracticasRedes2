#!/usr/bin/env python3
import socket
import selectors
import types
import time

HOST = "0.0.0.0"
PORT = 65432
INACTIVITY_TIMEOUT = 15.0  # Segundos de inactividad antes de borrar el sensor

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
                # Actualizar el temporizador de inactividad
                data.last_active = time.time()
                mensaje = recv_data.decode('utf-8').strip()
                
                if "," in mensaje:
                    parts = mensaje.split(",", 1)
                    data.sensor_id = parts[0].strip()
                    valor = parts[1].strip()
                    print(f"Sensor {data.sensor_id} reporta: {valor}")
                else:
                    print(f"Recibido de {data.addr}: {mensaje}")
                
                # Opcional: Responder al cliente
                sock.sendall(b"OK")
            else:
                # El cliente cerró la conexión ordenadamente (ej. Ctrl+C)
                close_connection(sock, data, motivo="Desconectado por el cliente")
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            # El cliente se cayó o cerró bruscamente
            close_connection(sock, data, motivo="Conexión interrumpida abruptamente")

def close_connection(sock, data, motivo="Timeout / Inactividad"):
    global active_sensors_count
    print(f"\n[-] {motivo} - Sensor ID: {data.sensor_id or 'Desconocido'} ({data.addr})")
    try:
        sel.unregister(sock)
    except Exception:
        pass
    sock.close()
    active_sensors_count = max(0, active_sensors_count - 1)
    print(f"📊 Número de sensores activos: {active_sensors_count}")

def check_timeouts():
    """Revisa si algún sensor superó el tiempo límite sin enviar datos."""
    current_time = time.time()
    # Usamos list() para evitar errores al modificar el diccionario mientras se itera
    for key in list(sel.get_map().values()):
        data = key.data
        if data is not None:  # Ignorar el socket principal del servidor
            if current_time - data.last_active > INACTIVITY_TIMEOUT:
                close_connection(key.fileobj, data, motivo="Timeout de inactividad alcanzado")

# --- Configuración del socket servidor ---
sock_accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_accept.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_accept.bind((HOST, PORT))
sock_accept.listen()
sock_accept.setblocking(False)

sel.register(sock_accept, selectors.EVENT_READ, data=None)

print(f"Servidor de sensores TCP iniciado en {HOST}:{PORT}")
print(f"Esperando conexiones... (Timeout de inactividad: {INACTIVITY_TIMEOUT}s)")

try:
    while True:
        # El select tiene timeout de 1s para permitir evaluar los timeouts periódicamente
        events = sel.select(timeout=1.0)
        
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
                
        # Verificar inactividades en cada ciclo
        check_timeouts()
        
except KeyboardInterrupt:
    print("\nServidor detenido manualmente.")
finally:
    sel.close()