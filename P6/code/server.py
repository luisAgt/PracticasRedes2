#!/usr/bin/env python3
import socket
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT_TCP = 7000
PORT_UDP_NAV = 5000
PORT_UDP_CHAT = 6000
BUFFER_SIZE = 1024

STORAGE_DIR = "archivos"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# TCP Socket
server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_tcp.bind((HOST, PORT_TCP))
server_tcp.listen(30)
server_tcp.setblocking(False)

# UDP Sockets
udp_nav = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_nav.bind((HOST, PORT_UDP_NAV))
udp_nav.setblocking(False)

udp_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_chat.bind((HOST, PORT_UDP_CHAT))
udp_chat.setblocking(False)

print(f"[SERVER STARTED] TCP: {PORT_TCP} | UDP Nav: {PORT_UDP_NAV} | UDP Chat: {PORT_UDP_CHAT}")

active_tcp_connections = []

try:
    while True:
        # 1. Accept new TCP connections
        try:
            conn, addr = server_tcp.accept()
            conn.setblocking(False)
            active_tcp_connections.append((conn, addr))
            print(f"[SUCCESS] New TCP connection accepted from {addr}")
        except BlockingIOError:
            pass

        # 2. Process active TCP clients (Query and Update)
        for conn, addr in active_tcp_connections[:]:
            try:
                data = conn.recv(BUFFER_SIZE)
                if data:
                    msg = data.decode("utf-8", errors="ignore").strip()
                    print(f"[TCP DATA] Received from {addr}: {msg}")

                    if msg.upper() in ["EXIT", "QUIT"]:
                        conn.sendall(b"[SUCCESS] Connection closed successfully.")
                        active_tcp_connections.remove((conn, addr))
                        conn.close()
                    elif msg.upper() == "QUERY_TIME":
                        now = datetime.now().strftime("%H:%M:%S")
                        conn.sendall(f"[SUCCESS] Current time: {now}".encode("utf-8"))
                    elif msg.upper() == "QUERY_DATE":
                        today = datetime.now().strftime("%Y-%m-%d")
                        conn.sendall(f"[SUCCESS] Current date: {today}".encode("utf-8"))
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

        # 3. Process UDP Notifications (Port 5000)
        try:
            data, addr = udp_nav.recvfrom(BUFFER_SIZE)
            print(f"[UDP NOTIFICATION - Port 5000] From {addr}: {data.decode('utf-8')}")
            udp_nav.sendto(b"[SUCCESS] Notification received on Port 5000.", addr)
        except BlockingIOError:
            pass

        # 4. Process UDP Notifications (Port 6000)
        try:
            data, addr = udp_chat.recvfrom(BUFFER_SIZE)
            print(f"[UDP NOTIFICATION - Port 6000] From {addr}: {data.decode('utf-8')}")
            udp_chat.sendto(b"[SUCCESS] Notification received on Port 6000.", addr)
        except BlockingIOError:
            pass

except KeyboardInterrupt:
    print("\n[SERVER STOPPED] Shutting down server...")
    server_tcp.close()
    udp_nav.close()
    udp_chat.close()