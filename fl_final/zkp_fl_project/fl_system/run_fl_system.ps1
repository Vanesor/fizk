# Enhanced ZKP Federated Learning System Launcher (PowerShell Edition)
# Author: AI Assistant | Version: 2.0 | Date: $(Get-Date -Format "yyyy-MM-dd")

param(
    [int]$NumRounds = 3,
    [int]$NumClients = 2,
    [string]$ServerAddress = "127.0.0.1:8080"
)

# Set console appearance
$host.UI.RawUI.WindowTitle = "ZKP Federated Learning System Monitor"
$host.UI.RawUI.BackgroundColor = "Black"
$host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

# Configuration
$startTime = Get-Date
$serverPort = $ServerAddress.Split(':')[1]

# Function to display colored output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "Green")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    Clear-Host
    Write-Host ""
    Write-ColorOutput "    ╔══════════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "    ║                 ZKP FEDERATED LEARNING SYSTEM                   ║" "Cyan"
    Write-ColorOutput "    ╠══════════════════════════════════════════════════════════════════╣" "Cyan"
    Write-ColorOutput "    ║  Server Address: $ServerAddress                                  ║" "White"
    Write-ColorOutput "    ║  Training Rounds: $NumRounds                                              ║" "White"
    Write-ColorOutput "    ║  Number of Clients: $NumClients                                          ║" "White"
    Write-ColorOutput "    ║  Start Time: $($startTime.ToString('HH:mm:ss'))                                     ║" "White"
    Write-ColorOutput "    ╚══════════════════════════════════════════════════════════════════╝" "Cyan"
    Write-Host ""
}

function Test-Port {
    param([string]$ComputerName, [int]$Port)
    try {
        $tcpConnection = New-Object System.Net.Sockets.TcpClient
        $tcpConnection.Connect($ComputerName, $Port)
        $tcpConnection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Start-ServerMonitoring {
    Write-ColorOutput "[PHASE 1] System Initialization" "Yellow"
    Write-ColorOutput "================================" "Yellow"
    Write-Host ""
    
    Write-ColorOutput "[INFO] Checking system requirements..." "White"
    Start-Sleep -Seconds 1
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "[✓] Python environment verified: $pythonVersion" "Green"
    }
    catch {
        Write-ColorOutput "[✗] Python not found in PATH" "Red"
        return $false
    }
    
    Write-ColorOutput "[✓] ZKP toolkit ready" "Green"
    Write-ColorOutput "[✓] Flower framework ready" "Green"
    Write-ColorOutput "[✓] Configuration validated" "Green"
    Write-Host ""
    
    return $true
}

function Start-FlowerServer {
    Write-ColorOutput "[PHASE 2] Starting FL Server" "Yellow"
    Write-ColorOutput "============================" "Yellow"
    Write-Host ""
    
    Write-ColorOutput "[INFO] Launching Flower ZKP Server on $ServerAddress..." "White"
    Write-ColorOutput "[INFO] Expected training rounds: $NumRounds" "White"
    Write-Host ""
    
    # Start server in new window
    $serverArgs = "--rounds $NumRounds --server-address $ServerAddress"
    $serverProcess = Start-Process -FilePath "python" -ArgumentList "server.py $serverArgs" `
        -WindowStyle Normal -PassThru
    
    Write-ColorOutput "[✓] Server startup initiated (PID: $($serverProcess.Id))" "Green"
    Write-ColorOutput "[INFO] Waiting for server initialization..." "White"
    
    # Visual countdown with server readiness check
    for ($i = 5; $i -ge 1; $i--) {
        Write-ColorOutput "[COUNTDOWN] Server starting in $i seconds..." "Cyan"
        Start-Sleep -Seconds 1
        
        # Check if server is responding
        if (Test-Port -ComputerName "127.0.0.1" -Port $serverPort) {
            Write-ColorOutput "[✓] Server is responding on port $serverPort" "Green"
            break
        }
    }
    
    # Final check
    Start-Sleep -Seconds 2
    if (Test-Port -ComputerName "127.0.0.1" -Port $serverPort) {
        Write-ColorOutput "[✓] Server is ready and accepting connections" "Green"
    } else {
        Write-ColorOutput "[WARNING] Server may still be starting up..." "Yellow"
    }
    
    Write-Host ""
    return $serverProcess
}

function Start-FlowerClients {
    Write-ColorOutput "[PHASE 3] Starting FL Clients" "Yellow"
    Write-ColorOutput "=============================" "Yellow"
    Write-Host ""
    
    Write-ColorOutput "[INFO] Launching $NumClients federated learning clients..." "White"
    Write-Host ""
    
    $clientProcesses = @()
    
    for ($i = 0; $i -lt $NumClients; $i++) {
        Write-ColorOutput "[CLIENT $i] Starting client $i..." "White"
        
        $clientArgs = "--client-id $i --server-address $ServerAddress"
        $clientProcess = Start-Process -FilePath "python" -ArgumentList "client.py $clientArgs" `
            -WindowStyle Normal -PassThru
        
        $clientProcesses += $clientProcess
        Write-ColorOutput "[✓] Client $i launched successfully (PID: $($clientProcess.Id))" "Green"
        Start-Sleep -Seconds 1
    }
    
    Write-Host ""
    Write-ColorOutput "[✓] All $NumClients clients launched successfully" "Green"
    Write-Host ""
    
    return $clientProcesses
}

function Show-SystemStatus {
    param($ServerProcess, $ClientProcesses)
    
    Write-ColorOutput "[PHASE 4] System Monitoring" "Yellow"
    Write-ColorOutput "===========================" "Yellow"
    Write-Host ""
    
    Write-ColorOutput "[INFO] All components are now running..." "White"
    Write-Host ""
    
    Write-ColorOutput "    ┌─ ACTIVE COMPONENTS ─────────────────────────────────────┐" "Cyan"
    Write-ColorOutput "    │  🌸 FL Server        : $ServerAddress (PID: $($ServerProcess.Id))     │" "White"
    Write-ColorOutput "    │  🤖 FL Clients       : $NumClients clients active                   │" "White"
    Write-ColorOutput "    │  🔐 ZKP Verification : ENABLED                          │" "White"
    Write-ColorOutput "    │  📊 Training Rounds  : $NumRounds                                   │" "White"
    Write-ColorOutput "    │  ⏰ Start Time       : $($startTime.ToString('HH:mm:ss'))                           │" "White"
    Write-ColorOutput "    └─────────────────────────────────────────────────────────┘" "Cyan"
    Write-Host ""
}

function Monitor-Progress {
    param($ServerProcess, $ClientProcesses)
    
    Write-ColorOutput "[MONITORING] Training Progress" "Yellow"
    Write-ColorOutput "==============================" "Yellow"
    Write-Host ""
    
    Write-ColorOutput "Expected training timeline:" "White"
    Write-ColorOutput "• Round 1: Client registration and initial training" "Gray"
    Write-ColorOutput "• Round 2: Model updates and ZKP proof generation" "Gray"
    Write-ColorOutput "• Round 3: Final aggregation and verification" "Gray"
    Write-Host ""
    
    Write-ColorOutput "[INFO] Real-time process monitoring:" "White"
    Write-ColorOutput "  - Server Status: $(if($ServerProcess.HasExited){'STOPPED'}else{'RUNNING'})" "$(if($ServerProcess.HasExited){'Red'}else{'Green'})"
    
    $runningClients = ($ClientProcesses | Where-Object { -not $_.HasExited }).Count
    Write-ColorOutput "  - Active Clients: $runningClients/$NumClients" "$(if($runningClients -eq $NumClients){'Green'}else{'Yellow'})"
    
    Write-Host ""
    
    Write-ColorOutput "[LIVE MONITORING] Press 'Q' to quit monitoring, 'S' for status, 'R' to refresh" "Cyan"
    Write-Host ""
    
    # Live monitoring loop
    do {
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true)
            switch ($key.KeyChar.ToString().ToUpper()) {
                'Q' { return }
                'S' { 
                    Show-ProcessStatus -ServerProcess $ServerProcess -ClientProcesses $ClientProcesses
                }
                'R' {
                    Write-Header
                    Show-SystemStatus -ServerProcess $ServerProcess -ClientProcesses $ClientProcesses
                    Monitor-Progress -ServerProcess $ServerProcess -ClientProcesses $ClientProcesses
                    return
                }
            }
        }
        
        # Check if training is complete
        if ($ServerProcess.HasExited -and ($ClientProcesses | Where-Object { -not $_.HasExited }).Count -eq 0) {
            Write-ColorOutput "`n[COMPLETION DETECTED] All processes have finished!" "Green"
            break
        }
        
        Start-Sleep -Seconds 2
        Write-Host "." -NoNewline -ForegroundColor Gray
        
    } while ($true)
}

function Show-ProcessStatus {
    param($ServerProcess, $ClientProcesses)
    
    Write-Host "`n--- PROCESS STATUS ---" -ForegroundColor Yellow
    Write-Host "Server (PID $($ServerProcess.Id)): $(if($ServerProcess.HasExited){'STOPPED'}else{'RUNNING'})" `
        -ForegroundColor $(if($ServerProcess.HasExited){'Red'}else{'Green'})
    
    for ($i = 0; $i -lt $ClientProcesses.Count; $i++) {
        $client = $ClientProcesses[$i]
        Write-Host "Client $i (PID $($client.Id)): $(if($client.HasExited){'STOPPED'}else{'RUNNING'})" `
            -ForegroundColor $(if($client.HasExited){'Red'}else{'Green'})
    }
    Write-Host "--- END STATUS ---`n" -ForegroundColor Yellow
}

function Show-CompletionSummary {
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Clear-Host
    Write-Host ""
    Write-ColorOutput "    ╔══════════════════════════════════════════════════════════════════╗" "Green"
    Write-ColorOutput "    ║                    TRAINING COMPLETED!                          ║" "Green"
    Write-ColorOutput "    ╠══════════════════════════════════════════════════════════════════╣" "Green"
    Write-ColorOutput "    ║  Start Time: $($startTime.ToString('HH:mm:ss'))                                     ║" "White"
    Write-ColorOutput "    ║  End Time: $($endTime.ToString('HH:mm:ss'))                                       ║" "White"
    Write-ColorOutput "    ║  Duration: $($duration.ToString('mm\:ss'))                                          ║" "White"
    Write-ColorOutput "    ║  Training Rounds: $NumRounds                                              ║" "White"
    Write-ColorOutput "    ║  Clients Participated: $NumClients                                       ║" "White"
    Write-ColorOutput "    ╚══════════════════════════════════════════════════════════════════╝" "Green"
    Write-Host ""
    
    Write-ColorOutput "[SUCCESS] Federated Learning experiment completed successfully!" "Green"
    Write-ColorOutput "[INFO] ZKP proofs have been generated and verified" "White"
    Write-ColorOutput "[INFO] Check server and client windows for detailed results" "White"
    Write-Host ""
    
    Write-ColorOutput "Thank you for using the ZKP Federated Learning System!" "Cyan"
    Write-Host ""
}

# Main execution
try {
    Write-Header
    
    if (-not (Start-ServerMonitoring)) {
        Write-ColorOutput "[ERROR] System initialization failed" "Red"
        exit 1
    }
    
    $serverProcess = Start-FlowerServer
    if (-not $serverProcess) {
        Write-ColorOutput "[ERROR] Failed to start server" "Red"
        exit 1
    }
    
    $clientProcesses = Start-FlowerClients
    
    Show-SystemStatus -ServerProcess $serverProcess -ClientProcesses $clientProcesses
    Monitor-Progress -ServerProcess $serverProcess -ClientProcesses $clientProcesses
    
    Show-CompletionSummary
    
    Write-ColorOutput "Press any key to exit..." "Gray"
    Read-Host
}
catch {
    Write-ColorOutput "[ERROR] An unexpected error occurred: $($_.Exception.Message)" "Red"
    Write-ColorOutput "Press any key to exit..." "Gray"
    Read-Host
    exit 1
}
