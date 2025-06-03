@echo off
title ZKP FL System - Launcher Selection
color 0B

echo.
echo    ╔══════════════════════════════════════════════════════════════════╗
echo    ║              ZKP FEDERATED LEARNING SYSTEM LAUNCHER             ║
echo    ╚══════════════════════════════════════════════════════════════════╝
echo.
echo Choose your preferred launcher:
echo.
echo    [1] Enhanced Batch Version (run_fl_system.bat)
echo        • Compatible with all Windows systems
echo        • Visual interface with progress monitoring
echo        • Automatic component management
echo.
echo    [2] PowerShell Version (run_fl_system.ps1) 
echo        • Advanced real-time monitoring
echo        • Process status tracking
echo        • Interactive controls (Q/S/R keys)
echo        • Colored output and better formatting
echo.
echo    [3] Quick Start (Original simple version)
echo        • Basic startup without monitoring
echo        • Minimal output
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Launching Enhanced Batch Version...
    call run_fl_system.bat
) else if "%choice%"=="2" (
    echo.
    echo [INFO] Launching PowerShell Version...
    echo [NOTE] You may need to allow PowerShell execution policy
    powershell -ExecutionPolicy Bypass -File "run_fl_system.ps1"
) else if "%choice%"=="3" (
    echo.
    echo [INFO] Quick Start - Launching basic version...
    echo Starting Flower ZKP Server...
    start "FL_Server" cmd /c "python server.py --rounds 3 --server-address 127.0.0.1:8080"
    timeout /t 5 /nobreak > nul
    echo Starting 2 Flower ZKP Clients...
    FOR /L %%i IN (0,1,1) DO (
        start "FL_Client_%%i" cmd /c "python client.py --client-id %%i --server-address 127.0.0.1:8080"
    )
    echo All components started.
) else (
    echo.
    echo [ERROR] Invalid choice. Please run the launcher again.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Launcher completed successfully!
pause
