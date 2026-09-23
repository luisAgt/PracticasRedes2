#!/bin/bash
SERVER_IP="192.168.1.32" # IP de la Máquina A

echo "[MACHINE C] Launching 5 Query Clients (Port 5000)..."
for i in {6..10}; do
    python3 client_query.py $SERVER_IP $i &
done

echo "[MACHINE C] Launching 2 Update Clients (Port 5000)..."
for i in {4..5}; do
    python3 client_update.py $SERVER_IP $i &
done

echo "[MACHINE C] Launching 8 Notification Clients (Port 5001)..."
for i in {8..15}; do
    python3 client_notify.py $SERVER_IP $i &
done

wait
echo "[MACHINE C] All 15 local clients completed."