#!/usr/bin/env python3
import socket
import selectors
import types
import time

# Configuración de red del servidor
HOST = "0.0.0.0"
PORT = 65432

sel = selectors.DefaultSelector()
active_sensors_count = 0

def accept_wrapper(sock):
    """Acepta una nueva conexión de un sensor y la registra en el selector en modo no bloqueante."""
    global active_sensors_count
    sock_conn, addr = sock.accept()
    sock_conn.setblocking(False)
    
    # Estructura para guardar el estado del sensor
    data = types.SimpleNamespace(
        addr=addr, 
        sensor_id=None
    )
    
    sel.register(sock_conn, selectors.EVENT_READ, data=data)
    active_sensors_count += 1
    
    print(f"\n[+] Conectado a {addr}")
    print(f"📊 Número de sensores activos: {active_sensors_count}")

def service_connection(key, mask):
    """Procesa los datos recibidos desde el socket de un sensor o gestiona su desconexión."""
    global active_sensors_count
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                mensaje = recv_data.decode('utf-8').strip()
                
                # Procesamos el formato esperado: sensor_id, valor
                if "," in mensaje:
                    parts = mensaje.split(",", 1)
                    data.sensor_id = parts[0].strip()
                    valor = parts[1].strip()
                    print(f"Sensor {data.sensor_id} reporta: {valor}")
                else:
                    print(f"Recibido de {data.addr}: {mensaje}")
                
                # Opcional: Enviar confirmación al cliente
                sock.sendall(b"OK")
            else:
                # El cliente cerró la conexión ordenadamente
                close_connection(sock, data, motivo="Desconectado por el cliente")
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            # Error o interrupción imprevista por parte del cliente
            close_connection(sock, data, motivo="Conexión interrumpida abruptamente")

def close_connection(sock, data, motivo="Cerrado"):
    """Cierra la conexión con un sensor, lo desregistra del selector y actualiza el contador."""
    global active_sensors_count
    print(f"\n[-] {motivo} - Sensor ID: {data.sensor_id or 'Desconocido'} ({data.addr})")
    try:
        sel.unregister(sock)
    except Exception:
        pass
    sock.close()
    active_sensors_count = max(0, active_sensors_count - 1)
    print(f"📊 Número de sensores activos: {active_sensors_count}")

# --- Inicialización del Socket Servidor ---
sock_accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_accept.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_accept.bind((HOST, PORT))
sock_accept.listen()
sock_accept.setblocking(False)

# Registramos el socket de escucha en el selector
sel.register(sock_accept, selectors.EVENT_READ, data=None)

print(f"Servidor de sensores TCP iniciado en {HOST}:{PORT}")
print("Esperando conexiones y datos de sensores indefinidamente...")

try:
    while True:
        # El selector se queda esperando eventos de lectura de forma indefinida
        events = sel.select()
        
        for key, mask in events:
            if key.data is None:
                # Evento en el socket servidor -> Nueva conexión entrante
                accept_wrapper(key.fileobj)
            else:
                # Evento en el socket de un cliente -> Lectura de datos
                service_connection(key, mask)
                
except KeyboardInterrupt:
    print("\nServidor detenido manualmente.")
finally:
    sel.close()