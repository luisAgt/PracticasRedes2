#!/bin/bash
SERVER_IP="192.168.1.32" # IP de la Máquina A

echo "[MACHINE B] Launching 5 Query Clients (Port 5000)..."
for i in {1..5}; do
    python3 client_query.py $SERVER_IP $i &
done

echo "[MACHINE B] Launching 3 Update Clients (Port 5000)..."
for i in {1..3}; do
    python3 client_update.py $SERVER_IP $i &
done

echo "[MACHINE B] Launching 7 Notification Clients (Port 5001)..."
for i in {1..7}; do
    python3 client_notify.py $SERVER_IP $i &
done

wait
echo "[MACHINE B] All 15 local clients completed."