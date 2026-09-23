#!/usr/bin/env python3
import socket, sys, time

if len(sys.argv) < 3:
    print("[ERROR] Usage: python3 client_query.py <SERVER_IP> <CLIENT_ID>")
    sys.exit(1)

server_ip, client_id = sys.argv[1], sys.argv[2]
server_port = 5000

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print(f"[SUCCESS] Query Client #{client_id} connected to port {server_port}.")

    for cmd in ["QUERY_TIME", "QUERY_DATE"]:
        sock.sendall(cmd.encode("utf-8"))
        resp = sock.recv(1024)
        print(f"[RESPONSE Client #{client_id}] {resp.decode('utf-8')}")
        time.sleep(0.5)

    sock.sendall(b"EXIT")
    sock.close()
except Exception as e:
    print(f"[ERROR] Query Client #{client_id}: {e}")