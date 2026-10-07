#!/usr/bin/env python3

import socket
import threading
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 65432
MAX_CLIENTES = 5
buffer_size = 1024

# Estructura global para mantener la información de clientes conectados
# Almacenará tuplas: (Cliente_ID, Socket, Hilo)
conexiones_activas = []
# Candado para evitar inconsistencias si dos hilos modifican la lista al mismo tiempo
lock_conexiones = threading.Lock()

def monitor_conexiones():
    """Hilo dedicado a verificar la integridad de la lista de conexiones (Req. 10 y 11)"""
    while True:
        time.sleep(10)  # Revisa y muestra la tabla cada 10 segundos
        with lock_conexiones:
            # Purga de conexiones muertas para mantener integridad
            conexiones_vivas = []
            for conn_info in conexiones_activas:
                cliente_id, sock, hilo = conn_info
                if sock.fileno() != -1:
                    conexiones_vivas.append(conn_info)
            
            # Actualizamos la lista original con las que siguen vivas
            conexiones_activas[:] = conexiones_vivas

            # Imprimir tabla de administración de conexiones
            print("\n--- CONEXIONES ACTIVAS ---")
            print(f"{'Cliente':<10} | {'Socket':<8} | {'Hilo':<10}")
            print("-" * 34)
            for cliente_id, sock, hilo in conexiones_activas:
                print(f"{cliente_id:<10} | {sock.fileno():<8} | {hilo.name:<10}")
            print("-" * 34)
            print(f"Total conectados: {len(conexiones_activas)} / {MAX_CLIENTES}\n")

def manejar_cliente(conn, addr, cliente_id):
    """Función que ejecuta el hilo de cada cliente"""
    hilo_actual = threading.current_thread()
    print(f"[{hilo_actual.name}] {cliente_id} conectado desde {addr}")
    
    try:
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            
            text = data.decode("utf-8").strip()
            cmd_upper = text.upper()
            cmd_lower = text.lower()

            # Finalizar sesión
            if cmd_upper in ["SALIR", "ADIOS", "EXIT", "QUIT"]:
                print(f"[{hilo_actual.name}] {cliente_id} solicitó desconexión.")
                break
                
            # Commands to handle
            elif cmd_upper in ["HOLA", "HI"]:
                conn.sendall(b"Hola! Bienvenido al servidor TCP concurrente.")
                
            elif cmd_upper in ["HORA", "TIME"]:
                now = datetime.now().strftime("%H:%M:%S")
                conn.sendall(f"Hora actual: {now}".encode("utf-8"))
                
            elif cmd_upper in ["FECHA", "DATE"]:
                today = datetime.now().strftime("%Y-%m-%d")
                conn.sendall(f"Fecha actual: {today}".encode("utf-8"))
                
            elif cmd_upper in ["AYUDA", "HELP"]:
                help_text = "Comandos: HOLA, HORA, FECHA, PEDIR <comida>, AYUDA, SALIR"
                conn.sendall(help_text.encode("utf-8"))
                
            #   Simulación de concurrencia y pedidos
            elif cmd_lower.startswith("pedir ") or cmd_lower.startswith("order "):
                item = text.split(" ", 1)[1].strip()
                
                # Asignar tiempo de procesamiento según el pedido
                tiempo_espera = 2 # Tiempo base por defecto
                if "pizza" in item.lower():
                    tiempo_espera = 5
                elif "hamburguesa" in item.lower():
                    tiempo_espera = 3
                elif "cafe" in item.lower() or "café" in item.lower():
                    tiempo_espera = 4
                    
                print(f"[{hilo_actual.name}] Procesando: {item.capitalize()}")
                
                # Avisar al cliente que su pedido se está preparando
                conn.sendall(f"Recibido. Preparando {item}, tardará {tiempo_espera} segundos...".encode("utf-8"))
                
                # La solicitud tarda en procesarse
                time.sleep(tiempo_espera) 
                
                print(f"[{hilo_actual.name}] {item.capitalize()} terminada")

                # Mandar la respuesta final
                conn.sendall(f"PEDIDO LISTO: {item}".encode("utf-8"))
                
            else:
                conn.sendall(b"Command not recognized. Write HELP.")
                
    except Exception as e:
        print(f"[{hilo_actual.name}] Error with {cliente_id}: {e}")
    
    finally:
        # Se ejecuta cuando el cliente se desconecta o hay un error
        print(f"[{hilo_actual.name}] Finalizando conexión con {cliente_id}.")
        conn.close()
        
        # Eliminar cliente de la lista de conexiones activas de forma segura
        with lock_conexiones:
            conexiones_activas[:] = [c for c in conexiones_activas if c[1] != conn]

def iniciar_servidor():
    # Iniciar el hilo que monitorea la integridad de las conexiones
    monitor = threading.Thread(target=monitor_conexiones, daemon=True)
    monitor.start()
    
    contador_clientes = 1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPServerSocket.bind((HOST, PORT))
        TCPServerSocket.listen(MAX_CLIENTES)
        print(f"El servidor TCP multihilo está disponible en {HOST}:{PORT}")

        while True:
            # El servidor sigue aceptando conexiones mientras haya clientes atendidos
            client_conn, client_addr = TCPServerSocket.accept()
            
            with lock_conexiones:
                # Verificar límite de 5 clientes simultáneos
                if len(conexiones_activas) >= MAX_CLIENTES:
                    print(f"Servidor lleno. Rechazando nueva conexión de {client_addr}")
                    client_conn.sendall(b"ERROR: Servidor lleno (Max 5 clientes). Intenta de nuevo mas tarde.")
                    client_conn.close()
                    continue
                
                cliente_id = f"Cliente {contador_clientes}"
                contador_clientes += 1
                
                # Crear un hilo específico para atender al cliente conectado
                nombre_hilo = f"T{contador_clientes-1}"
                hilo_cliente = threading.Thread(
                    target=manejar_cliente, 
                    args=(client_conn, client_addr, cliente_id),
                    name=nombre_hilo
                )
                
                # Incorporar a la estructura de conexiones activas
                conexiones_activas.append((cliente_id, client_conn, hilo_cliente))
                hilo_cliente.start()

if __name__ == "__main__":
    iniciar_servidor()