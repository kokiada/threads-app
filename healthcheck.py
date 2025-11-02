#!/usr/bin/env python3
import socket
import sys
import os

def check_port(port):
    """指定されたポートが開いているか確認"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    frontend_port = int(os.getenv("PORT", 3000))
    backend_port = int(os.getenv("BACKEND_PORT", 8000))
    
    print(f"=== Health Check ===")
    print(f"Frontend port {frontend_port}: {'✓ OPEN' if check_port(frontend_port) else '✗ CLOSED'}")
    print(f"Backend port {backend_port}: {'✓ OPEN' if check_port(backend_port) else '✗ CLOSED'}")
    
    if check_port(frontend_port) and check_port(backend_port):
        print("Status: OK - Both ports are open")
        sys.exit(0)
    else:
        print("Status: ERROR - One or more ports are closed")
        sys.exit(1)

if __name__ == "__main__":
    main()
