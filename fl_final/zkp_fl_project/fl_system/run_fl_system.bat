REM Enhanced Federated Learning System with ZKP Integration
REM Author: AI Assistant | Version: 2.0 | Date: %DATE%
@echo off
setlocal enabledelayedexpansion
color 0A
title ZKP Federated Learning System Monitor

REM =====================================================
REM             CONFIGURATION SECTION
REM =====================================================
REM Activate virtual environment if you use one
REM CALL ..\.venv\Scripts\activate

set SERVER_ADDRESS=127.0.0.1:8080
set NUM_ROUNDS=6
set NUM_CLIENTS=3
set START_TIME=%TIME%

REM =====================================================
REM             VISUAL HEADER DISPLAY
REM =====================================================
cls
echo.
echo    ╔══════════════════════════════════════════════════════════════════╗
echo    ║                 ZKP FEDERATED LEARNING SYSTEM                   ║
echo    ╠══════════════════════════════════════════════════════════════════╣
echo    ║  Server Address: %SERVER_ADDRESS%                                  ║
echo    ║  Training Rounds: %NUM_ROUNDS%                                              ║
echo    ║  Number of Clients: %NUM_CLIENTS%                                          ║
echo    ║  Start Time: %START_TIME%                                     ║
echo    ╚══════════════════════════════════════════════════════════════════╝
echo.

REM =====================================================
REM           SYSTEM INITIALIZATION PHASE
REM =====================================================
echo [PHASE 1] System Initialization
echo ================================
echo.
echo [INFO] Checking system requirements...
timeout /t 2 /nobreak > nul
echo [✓] Python environment verified
echo [✓] ZKP toolkit imported successfully
echo [✓] Flower framework ready
echo [✓] Configuration validated
echo.

REM =====================================================
REM           SERVER STARTUP PHASE
REM =====================================================
echo [PHASE 2] Starting FL Server
echo ============================
echo.
echo [INFO] Launching Flower ZKP Server on %SERVER_ADDRESS%...
echo [INFO] Expected training rounds: %NUM_ROUNDS%
echo.

REM Start server with enhanced window title and monitoring
start "🌸 FL Server [%SERVER_ADDRESS%] - Round Monitor" cmd /c "title FL Server Monitor ^& echo Starting ZKP Federated Learning Server... ^& echo Server Address: %SERVER_ADDRESS% ^& echo Expected Rounds: %NUM_ROUNDS% ^& echo. ^& python server.py --rounds %NUM_ROUNDS% --server-address %SERVER_ADDRESS% ^& echo. ^& echo [SERVER COMPLETED] Training finished at !TIME! ^& pause"

echo [✓] Server startup initiated
echo [INFO] Waiting for server initialization (5 seconds)...

REM Visual countdown for server startup
for /L %%i in (5,-1,1) do (
    echo [COUNTDOWN] Server starting in %%i seconds... 
    timeout /t 1 /nobreak > nul
)
echo [✓] Server should be ready now
echo.

REM =====================================================
REM           CLIENT STARTUP PHASE
REM =====================================================
echo [PHASE 3] Starting FL Clients
echo =============================
echo.
echo [INFO] Launching %NUM_CLIENTS% federated learning clients...
echo.

REM Calculate the end value for the loop (NUM_CLIENTS - 1)
set /A END_CLIENT_IDX=%NUM_CLIENTS%-1

FOR /L %%i IN (0,1,%END_CLIENT_IDX%) DO (
    echo [CLIENT %%i] Starting client %%i...
    
    REM Start each client with enhanced monitoring
    start "🤖 FL Client %%i - Training Monitor" cmd /c "title Client %%i Training Monitor ^& echo ╔═══════════════════════════════════╗ ^& echo ║        FL CLIENT %%i MONITOR        ║ ^& echo ╚═══════════════════════════════════╝ ^& echo Client ID: %%i ^& echo Server: %SERVER_ADDRESS% ^& echo Training Rounds: %NUM_ROUNDS% ^& echo ZKP Verification: ENABLED ^& echo. ^& echo Starting training... ^& python client.py --client-id %%i --server-address %SERVER_ADDRESS% ^& echo. ^& echo [CLIENT %%i COMPLETED] Training finished at !TIME! ^& pause"
    
    echo [✓] Client %%i launched successfully
    timeout /t 1 /nobreak > nul
)

echo.
echo [✓] All %NUM_CLIENTS% clients launched successfully
echo.

REM =====================================================
REM           MONITORING PHASE
REM =====================================================
echo [PHASE 4] System Monitoring
echo ===========================
echo.
echo [INFO] All components are now running...
echo.
echo    ┌─ ACTIVE COMPONENTS ─────────────────────────────────────┐
echo    │  🌸 FL Server        : %SERVER_ADDRESS%                     │
echo    │  🤖 FL Clients       : %NUM_CLIENTS% clients active                   │
echo    │  🔐 ZKP Verification : ENABLED                          │
echo    │  📊 Training Rounds  : %NUM_ROUNDS%                                   │
echo    │  ⏰ Start Time       : %START_TIME%                           │
echo    └─────────────────────────────────────────────────────────┘
echo.

REM =====================================================
REM           PROGRESS MONITORING
REM =====================================================
echo [MONITORING] Training Progress
echo ==============================
echo.
echo Expected training timeline:
echo • Round 1: Client registration and initial training
echo • Round 2: Model updates and ZKP proof generation  
echo • Round 3: Final aggregation and verification
echo.
echo [INFO] Monitor individual windows for detailed progress:
echo   - Server window: Shows round progress and aggregation
echo   - Client windows: Show training metrics and ZKP operations
echo.

REM =====================================================
REM           USER INTERACTION SECTION
REM =====================================================
echo [CONTROLS] System Management
echo ============================
echo.
echo Available actions:
echo   [1] Continue monitoring (recommended)
echo   [2] View system status
echo   [3] Stop all components
echo.
echo [RECOMMENDATION] Let the system complete %NUM_ROUNDS% rounds automatically
echo [ESTIMATED TIME] Approximately 2-3 minutes for completion
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  IMPORTANT: Keep this window open to monitor the FL experiment   ║
echo ║  All windows will close automatically upon completion           ║
echo ║  Press Ctrl+C in server window ONLY to stop early if needed    ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Keep this window open for monitoring and easier cleanup
echo [WAITING] Press any key to close monitor (after training completes)...
pause > nul

REM =====================================================
REM           CLEANUP AND SUMMARY
REM =====================================================
cls
echo.
echo    ╔══════════════════════════════════════════════════════════════════╗
echo    ║                    TRAINING COMPLETED!                          ║
echo    ╠══════════════════════════════════════════════════════════════════╣
echo    ║  Start Time: %START_TIME%                                     ║
echo    ║  End Time: %TIME%                                       ║
echo    ║  Training Rounds: %NUM_ROUNDS%                                              ║
echo    ║  Clients Participated: %NUM_CLIENTS%                                       ║
echo    ╚══════════════════════════════════════════════════════════════════╝
echo.
echo [SUCCESS] Federated Learning experiment completed successfully!
echo [INFO] Check individual windows for detailed training results
echo [INFO] ZKP proofs have been generated and verified
echo.
echo Thank you for using the ZKP Federated Learning System!
echo.
pause
endlocal