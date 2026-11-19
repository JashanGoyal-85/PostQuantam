#!/usr/bin/env python3
"""
Lattice-Based Post-Quantum Cryptography — Live Presentation Server
Run this script to launch the interactive live demo for your presentation:
    python3 app.py
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Keep terminal clean during presentation
        pass

def find_available_port(start_port=8000, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def run_server():
    os.chdir(DIRECTORY)
    port = PORT
    try:
        # Check if port is available, else try next
        import socket
        port = find_available_port(PORT)
    except Exception:
        port = PORT

    url = f"http://127.0.0.1:{port}"
    print("=" * 70)
    print("🔐  LATTICE-BASED POST-QUANTUM CRYPTOGRAPHY — LIVE PRESENTATION DEMO")
    print("=" * 70)
    print(f"📡  Serving interactive lab at: {url}")
    print(f"📁  Serving files from:         {DIRECTORY}")
    print("=" * 70)
    print("💡  PRESENTATION QUICK ACTIONS:")
    print("   • Preset 1: 2D Lattice Trapdoor Geometry")
    print("   • Preset 2: N-D Babai 100D Accuracy Collapse (Gap A)")
    print("   • Preset 3: Deep Learning Voronoi Facet Collapse (Part B)")
    print("   • Preset 4: Live LWE Text Encrypt/Decrypt (Gap B)")
    print("   • Preset 5: Noise Overflow Attack (sigma -> 7.5)")
    print("   • Preset 6: Zero-Noise Eavesdropper Exploit (sigma -> 0)")
    print("=" * 70)
    print("Press Ctrl+C to stop the server.\n")

    # Open browser automatically after 0.5s
    def open_browser():
        time.sleep(0.5)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server. Presentation demo concluded.")
            httpd.server_close()

if __name__ == '__main__':
    run_server()
