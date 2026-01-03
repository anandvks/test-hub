@echo off
REM Documentation Server Launcher for Windows
REM Quick script to serve Test Bench GUI documentation locally

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
echo Starting documentation server...
echo.
echo Documentation will be available at:
echo    http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================
echo.

REM Start MkDocs server
mkdocs serve
