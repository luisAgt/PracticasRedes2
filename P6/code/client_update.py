#!/usr/bin/env python3
import socket, sys

if len(sys.argv) < 3:
    print("[ERROR] Usage: python3 client_update.py <SERVER_IP> <CLIENT_ID>")
    sys.exit(1)

server_ip, client_id = sys.argv[1], sys.argv[2]
server_port = 5000

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    payload = f"UPDATE_FILE: Data payload from Client #{client_id}"
    sock.sendall(payload.encode("utf-8"))
    resp = sock.recv(1024)
    print(f"[RESPONSE Client #{client_id}] {resp.decode('utf-8')}")
    sock.sendall(b"EXIT")
    sock.close()
except Exception as e:
    print(f"[ERROR] Update Client #{client_id}: {e}")