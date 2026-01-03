@echo off
REM Documentation Server Launcher for Windows
REM Quick script to serve Test Bench GUI documentation locally

setlocal enabledelayedexpansion

echo ================================
echo Test Bench GUI Documentation
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if MkDocs is installed
mkdocs --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] MkDocs not found. Installing...
    echo.
    pip install mkdocs mkdocs-material
    if errorlevel 1 (
        echo.
        echo Error: Failed to install MkDocs
        echo Try manually: pip install mkdocs mkdocs-material
        pause
        exit /b 1
    )
    echo.
    echo [OK] MkDocs installed successfully
) else (
    echo [OK] MkDocs found
)

echo.
echo Finding available port...

REM Function to check if port is in use
set PORT=8000
set MAX_PORT=8100
set PORT_FOUND=0

:find_port
if !PORT! gtr !MAX_PORT! (
    echo Error: No available ports found between 8000-8100
    echo Please free up some ports or specify a custom port
    pause
    exit /b 1
)

REM Check if port is in use using netstat
netstat -an | findstr "127.0.0.1:!PORT! " | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    REM Port is available
    set PORT_FOUND=1
    goto port_found
) else (
    REM Port is in use, try next one
    set /a PORT+=1
    goto find_port
)

:port_found
if !PORT! neq 8000 (
    echo [!] Port 8000 is in use, using port !PORT!
) else (
    echo [OK] Using port !PORT!
)

echo.
echo Starting documentation server...
echo.
echo Documentation will be available at:
echo    http://127.0.0.1:!PORT!/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================
echo.

REM Start MkDocs server
mkdocs serve --dev-addr=127.0.0.1:!PORT!
