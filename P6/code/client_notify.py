#!/usr/bin/env python3
import socket, sys

if len(sys.argv) < 3:
    print("[ERROR] Usage: python3 client_notify.py <SERVER_IP> <CLIENT_ID>")
    sys.exit(1)

server_ip, client_id = sys.argv[1], sys.argv[2]
dest_port = 5001

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = f"NOTIFICATION: Event alert from Client #{client_id}"
    sock.sendto(msg.encode("utf-8"), (server_ip, dest_port))
    sock.settimeout(2.0)
    data, addr = sock.recvfrom(1024)
    print(f"[RESPONSE Client #{client_id}] {data.decode('utf-8')}")
    sock.close()
except Exception as e:
    print(f"[ERROR] Notify Client #{client_id}: {e}")