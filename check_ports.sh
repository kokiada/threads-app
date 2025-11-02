#!/bin/bash

echo "=== Port Check ==="
echo "Checking processes on ports 3000 and 8000..."
echo ""

echo "Port 3000 (Frontend):"
lsof -i :3000 || echo "No process on port 3000"
echo ""

echo "Port 8000 (Backend):"
lsof -i :8000 || echo "No process on port 8000"
echo ""

echo "All Python processes:"
ps aux | grep python | grep -v grep
echo ""

echo "All Reflex processes:"
ps aux | grep reflex | grep -v grep
echo ""

echo "Listening ports:"
netstat -tuln | grep LISTEN || ss -tuln | grep LISTEN
