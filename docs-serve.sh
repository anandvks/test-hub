#!/bin/bash
# Documentation Server Launcher
# Quick script to serve Test Bench GUI documentation locally

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Bench GUI Documentation${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} MkDocs not found. Installing..."
    echo ""

    # Try to install MkDocs and Material theme
    if pip3 install mkdocs mkdocs-material; then
        echo ""
        echo -e "${GREEN}✓${NC} MkDocs installed successfully"
    else
        echo -e "${RED}Error: Failed to install MkDocs${NC}"
        echo "Try manually: pip3 install mkdocs mkdocs-material"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} MkDocs found: $(mkdocs --version | head -n1)"
fi

echo ""
echo -e "${BLUE}Finding available port...${NC}"

# Function to check if port is in use
is_port_in_use() {
    if command -v lsof &> /dev/null; then
        lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
    elif command -v netstat &> /dev/null; then
        netstat -an | grep -q ":$1.*LISTEN"
    else
        # Fallback: try to bind to the port
        python3 -c "import socket; s = socket.socket(); s.bind(('127.0.0.1', $1)); s.close()" 2>/dev/null
        return $?
    fi
}

# Find available port starting from 8000
PORT=8000
MAX_PORT=8100
PORT_FOUND=false

while [ $PORT -le $MAX_PORT ]; do
    if ! is_port_in_use $PORT; then
        PORT_FOUND=true
        break
    fi
    PORT=$((PORT + 1))
done

if [ "$PORT_FOUND" = false ]; then
    echo -e "${RED}Error: No available ports found between 8000-8100${NC}"
    echo "Please free up some ports or specify a custom port with:"
    echo "mkdocs serve --dev-addr=127.0.0.1:PORT"
    exit 1
fi

if [ $PORT -ne 8000 ]; then
    echo -e "${YELLOW}⚠${NC} Port 8000 is in use, using port ${PORT}"
else
    echo -e "${GREEN}✓${NC} Using port ${PORT}"
fi

echo ""
echo -e "${GREEN}Documentation will be available at:${NC}"
echo -e "${BLUE}➜${NC}  http://127.0.0.1:${PORT}/"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo "================================"
echo ""

# Start MkDocs server
mkdocs serve --dev-addr=127.0.0.1:$PORT
