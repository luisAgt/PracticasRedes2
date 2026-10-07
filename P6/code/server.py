#!/usr/bin/env python3
import socket
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT_TCP = 5000       # Consulta y Actualización
PORT_UDP_NOTIF = 5001 # Notificaciones
BUFFER_SIZE = 1024

STORAGE_DIR = "archivos"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# TCP Socket (Port 5000)
server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_tcp.bind((HOST, PORT_TCP))
server_tcp.listen(30)
server_tcp.setblocking(False)

# UDP Socket (Port 5001)
udp_notif = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_notif.bind((HOST, PORT_UDP_NOTIF))
udp_notif.setblocking(False)

print(f"[SERVER STARTED] TCP (Query/Update): {PORT_TCP} | UDP (Notify): {PORT_UDP_NOTIF}")

active_tcp_connections = []

try:
    while True:
        # 1. Accept new TCP connections on Port 5000
        try:
            conn, addr = server_tcp.accept()
            conn.setblocking(False)
            active_tcp_connections.append((conn, addr))
            print(f"[SUCCESS] New TCP connection accepted from {addr} on Port {PORT_TCP}")
        except BlockingIOError:
            pass

        # 2. Process active TCP clients (Query and Update)
        for conn, addr in active_tcp_connections[:]:
            try:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    msg = data.decode("utf-8", errors="ignore").strip()
                    print(f"[TCP DATA - Port 5000] Received from {addr}: {msg}")

                    if msg.upper() in ["EXIT", "QUIT"]:
                        conn.sendall(b"[SUCCESS] Connection closed successfully.")
                        active_tcp_connections.remove((conn, addr))
                        conn.close()

                    # Query commands
                    elif msg.upper() == "QUERY_TIME":
                        now = datetime.now().strftime("%H:%M:%S")
                        conn.sendall(f"[SUCCESS] Current time: {now}".encode("utf-8"))
                    elif msg.upper() == "QUERY_DATE":
                        today = datetime.now().strftime("%Y-%m-%d")
                        conn.sendall(f"[SUCCESS] Current date: {today}".encode("utf-8"))

                    # Update commands
                    elif msg.upper().startswith("UPDATE_FILE:"):
                        content = msg.split(":", 1)[1]
                        filename = f"update_{addr[1]}.txt"
                        filepath = os.path.join(STORAGE_DIR, filename)
                        with open(filepath, "a") as f:
                            f.write(content + "\n")
                        conn.sendall(b"[SUCCESS] File updated successfully.")
                    else:
                        conn.sendall(b"[ERROR] Command not recognized.")
                else:
                    print(f"[INFO] Client {addr} disconnected.")
                    active_tcp_connections.remove((conn, addr))
                    conn.close()
            except BlockingIOError:
                pass
            except ConnectionResetError:
                print(f"[ERROR] Connection lost with {addr}")
                active_tcp_connections.remove((conn, addr))
                conn.close()

        # 3. Process UDP Notifications on Port 5001
        try:
            data, addr = udp_notif.recvfrom(BUFFER_SIZE)
            print(f"[UDP NOTIFICATION - Port 5001] Received from {addr}: {data.decode('utf-8')}")
            udp_notif.sendto(b"[SUCCESS] Notification received on Port 5001.", addr)
        except BlockingIOError:
            pass

except KeyboardInterrupt:
    print("\n[SERVER STOPPED] Shutting down server...")
    server_tcp.close()
    udp_notif.close()