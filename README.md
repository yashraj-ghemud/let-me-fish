# Evil Twin Framework v2.0

Educational Security Testing Tool for WiFi Security Assessment

## ⚠️ DISCLAIMER

**This tool is for EDUCATIONAL PURPOSES ONLY.** Use only on networks you own or have explicit permission to test. Unauthorized access to computer networks is illegal and can result in severe legal consequences.

## 📋 Overview

The Evil Twin Framework automates the creation of a Rogue Access Point with a Captive Portal for educational security testing. It integrates with the existing `ghost-kicker.sh` deauthentication tool to provide a complete Evil Twin attack simulation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Orchestrator                      │
│                        (main.py)                          │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┼────────┬────────────┬──────────────┐
    │        │        │            │              │
┌───▼───┐ ┌─▼──────┐ ┌─▼────────┐ ┌─▼──────────┐ ┌─▼─────────┐
│Deauther│ │hostapd │ │ dnsmasq  │ │ Flask App  │ │ iptables  │
│(Scapy) │ │ (Fake  │ │ (DHCP+   │ │ (Captive   │ │ (Traffic  │
│        │ │  AP)   │ │  DNS)    │ │  Portal)   │ │  Redirect)│
└───────┘ └────────┘ └──────────┘ └────────────┘ └───────────┘
```

## 🔧 Components

### 1. **main.py** - Core Orchestrator
- Manages all concurrent processes
- Handles hardware configuration (interface, channel, IP)
- Manages iptables rules for traffic redirection
- Implements graceful cleanup on Ctrl+C

### 2. **deauther.py** - Scapy-based Deauther
- Sends deauthentication packets to target AP
- Supports broadcast and targeted deauth
- Continuous mode with configurable interval

### 3. **hostapd** - Fake Access Point
- Creates rogue AP with same SSID as target
- Open network (no authentication)
- Configurable channel and hardware mode

### 4. **dnsmasq** - Network Manager
- DHCP server for assigning IPs to victims
- DNS server redirecting all queries to local IP
- DNS sinkhole implementation

### 5. **captive_portal.py** - Flask Web Server
- Runs on port 80
- Fake router firmware update login page
- Captures credentials (username, password, SSID)
- Logs all captured data to `log.txt`

### 6. **ghost-kicker.sh** - Deauthentication Tool
- Existing WiFi deauthentication tool
- Can be used independently or with the framework
- Scans networks and performs targeted attacks

## 📦 Dependencies

### System Tools
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y hostapd dnsmasq iptables python3-pip

# Arch Linux
sudo pacman -S hostapd dnsmasq iptables python-pip

# Kali Linux (pre-installed)
# Just ensure hostapd and dnsmasq are present
```

### Python Packages
```bash
pip3 install -r requirements.txt
```

## 🚀 Setup Instructions

### 1. Clone/Download the Framework
```bash
cd "ewil twin"
```

### 2. Install Python Dependencies
```bash
pip3 install flask scapy
```

### 3. Verify System Tools
```bash
# Check hostapd
hostapd -v

# Check dnsmasq
dnsmasq --version

# Check iptables
iptables --version
```

### 4. Prepare Wireless Interface
```bash
# Enable monitor mode (you can use ghost-kicker.sh for this)
sudo ./ghost-kicker.sh
# Select option 1 to enable monitor mode
```

## 🎯 Usage

### Using the Full Framework (main.py)

```bash
# Run as root
sudo python3 main.py
```

**The framework will prompt for:**
- Wireless interface (e.g., wlan0mon)
- Target BSSID (AP MAC address)
- Target SSID (network name)
- Target channel
- Gateway IP (default: 10.0.0.1)

**What happens:**
1. Interface is configured on target channel
2. IP address is assigned to interface
3. IP forwarding is enabled
4. iptables rules are set up for traffic redirection
5. hostapd starts the fake AP
6. dnsmasq starts DHCP/DNS services
7. Flask captive portal starts on port 80
8. Deauther starts jamming the original AP
9. Victims connect to fake AP and see the login page
10. Credentials are captured to `log.txt`

### Using Individual Components

#### Deauther Only (Scapy)
```bash
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon
```

**Options:**
- `--bssid`: Target AP MAC address (required)
- `--interface`: Wireless interface in monitor mode (required)
- `--client`: Target client MAC (for targeted attack)
- `--count`: Number of packets (default: 100)
- `--interval`: Interval for continuous mode (default: 2)
- `--continuous`: Enable continuous deauth mode

#### Captive Portal Only
```bash
sudo python3 captive_portal.py
```

#### Using ghost-kicker.sh (Deauth Tool)
```bash
sudo ./ghost-kicker.sh
```

**Menu Options:**
1. Enable Monitor Mode
2. Scan Networks
3. Target Specific Attack
4. Chaos Mode (Deauth All Clients)
5. Disable Monitor Mode & Exit

## 📁 Project Structure

```
ewil twin/
├── main.py                 # Core orchestrator
├── deauther.py            # Scapy deauther
├── captive_portal.py      # Flask captive portal
├── ghost-kicker.sh        # Bash deauth tool
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config/
│   ├── hostapd.conf      # hostapd template
│   └── dnsmasq.conf      # dnsmasq template
├── templates/
│   └── login.html        # Fake login page
└── log.txt               # Captured credentials (created during runtime)
```

## 🔐 Security Considerations

### What This Tool Does
- Creates a fake WiFi access point
- Deauthenticates clients from real AP
- Intercepts DHCP and DNS requests
- Displays a fake login page
- Captures credentials entered by users

### Legal Warning
- **ONLY use on networks you own**
- **Get explicit written permission before testing**
- **Unauthorized use is illegal in most jurisdictions**
- **This is for educational purposes only**

### Defensive Measures
To protect against Evil Twin attacks:
1. Use WPA3 or WPA2-Enterprise with certificate authentication
2. Enable AP isolation on public networks
3. Use VPNs when connecting to public WiFi
4. Verify SSL certificates on all websites
5. Use network security monitoring tools

## 🛠️ Troubleshooting

### hostapd fails to start
```bash
# Check if interface is in monitor mode
iwconfig

# Ensure no other hostapd instance is running
sudo killall hostapd

# Check hostapd configuration
sudo hostapd -dd config/hostapd.conf
```

### dnsmasq fails to start
```bash
# Kill existing dnsmasq
sudo killall dnsmasq

# Check configuration
sudo dnsmasq -C config/dnsmasq.conf --test
```

### Flask won't bind to port 80
```bash
# Check if port 80 is in use
sudo netstat -tulpn | grep :80

# Kill process using port 80
sudo killall python3
```

### Clients not getting IP addresses
```bash
# Check dnsmasq logs
sudo journalctl -u dnsmasq -f

# Verify interface has IP
ip addr show wlan0mon
```

### Cleanup failed
```bash
# Manual cleanup
sudo killall hostapd dnsmasq python3
sudo iptables -F
sudo iptables -t nat -F
sudo sysctl -w net.ipv4.ip_forward=0
sudo systemctl restart NetworkManager
```

## 📊 Captured Credentials Format

Credentials are saved to `log.txt` in the following format:
```
[2024-04-09 12:34:56] Username: user@example.com | Password: mypassword123 | SSID: TargetNetwork | Client IP: 10.0.0.15
```

## 🔧 Customization

### Modify the Login Page
Edit `templates/login.html` or the `LOGIN_HTML` variable in `captive_portal.py` to change the appearance and fields of the captive portal.

### Change DHCP Range
Modify the `dhcp-range` in `config/dnsmasq.conf` or update the `target_config` dictionary in `main.py`.

### Change Gateway IP
Update the `gateway_ip`, `dhcp_start`, and `dhcp_end` values in `main.py`.

## 📚 Educational Resources

- [WiFi Security Basics](https://www.kali.org/tools/aircrack-ng/)
- [Evil Twin Attack Explained](https://en.wikipedia.org/wiki/Evil_twin_(wireless_networks))
- [Captive Portal Security](https://owasp.org/www-community/attacks/Captive_Portal)

## 🤝 Contributing

This is an educational project. Feel free to submit issues or pull requests for improvements.

## ⚖️ License

This project is for educational purposes only. Use responsibly and legally.

## 📞 Support

For issues or questions, please refer to the troubleshooting section above.

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
"# let-me-fish" 
