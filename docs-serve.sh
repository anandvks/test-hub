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
echo -e "${BLUE}Starting documentation server...${NC}"
echo ""

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC} Port 8000 is already in use"
    echo "Using alternative port 8001"
    PORT=8001
else
    PORT=8000
fi

echo -e "${GREEN}Documentation will be available at:${NC}"
echo -e "${BLUE}➜${NC}  http://127.0.0.1:${PORT}/"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo "================================"
echo ""

# Start MkDocs server
if [ "$PORT" = "8000" ]; then
    mkdocs serve
else
    mkdocs serve --dev-addr=127.0.0.1:$PORT
fi
