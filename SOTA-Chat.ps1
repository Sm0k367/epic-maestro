# SOTA Chat CLI - PowerShell Interactive Chat Client
# Simple, reliable version for PowerShell 5.0+

param(
    [string]$ApiUrl = "http://localhost:8800",
    [string]$UserId = "ps-user"
)

# Configuration
$ChatEndpoint = "$ApiUrl/api/chat"
$HistoryEndpoint = "$ApiUrl/api/chat/history/$UserId"
$SessionStart = Get-Date

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      SOTA Chat CLI                            ║" -ForegroundColor Cyan
Write-Host "║        State-of-the-Art Orchestration Agent                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] User ID: $UserId" -ForegroundColor Green
Write-Host "[INFO] API URL: $ApiUrl" -ForegroundColor Green
Write-Host "[INFO] Type '/help' for commands or start chatting" -ForegroundColor Green
Write-Host ""

# Check connection
try {
    $null = Invoke-WebRequest -Uri "$ApiUrl/docs" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[SUCCESS] Connected to SOTA API" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Could not connect to SOTA at $ApiUrl" -ForegroundColor Red
    Write-Host "[ERROR] Make sure Docker containers are running: docker-compose up -d" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Message counter
$MessageCount = 0

# Main chat loop
while ($true) {
    # Prompt
    Write-Host "You > " -ForegroundColor White -NoNewline
    $UserInput = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($UserInput)) {
        continue
    }
    
    # Handle commands
    if ($UserInput -eq "/exit") {
        Write-Host ""
        Write-Host "[INFO] Thank you for using SOTA Chat CLI!" -ForegroundColor Green
        $Uptime = (Get-Date) - $SessionStart
        Write-Host "[INFO] Session duration: $($Uptime.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        Write-Host "[INFO] Messages sent: $MessageCount" -ForegroundColor Green
        Write-Host ""
        break
    }
    elseif ($UserInput -eq "/help") {
        Write-Host ""
        Write-Host "════ Available Commands ════" -ForegroundColor Cyan
        Write-Host "  /help      - Show this help message" -ForegroundColor Green
        Write-Host "  /clear     - Clear the screen" -ForegroundColor Green
        Write-Host "  /status    - Show connection status" -ForegroundColor Green
        Write-Host "  /history   - Show conversation history" -ForegroundColor Green
        Write-Host "  /exit      - Exit the chat" -ForegroundColor Green
        Write-Host ""
        Write-Host "════ Example Queries ════" -ForegroundColor Cyan
        Write-Host "  • System health" -ForegroundColor Green
        Write-Host "  • Infer best approach" -ForegroundColor Green
        Write-Host "  • Stitch video files" -ForegroundColor Green
        Write-Host "  • Broadcast to workers" -ForegroundColor Green
        Write-Host "  • Learn patterns" -ForegroundColor Green
        Write-Host "  • Detect failures" -ForegroundColor Green
        Write-Host "  • Improve performance" -ForegroundColor Green
        Write-Host ""
    }
    elseif ($UserInput -eq "/clear") {
        Clear-Host
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║                      SOTA Chat CLI                            ║" -ForegroundColor Cyan
        Write-Host "║        State-of-the-Art Orchestration Agent                  ║" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
    }
    elseif ($UserInput -eq "/status") {
        Write-Host ""
        Write-Host "════ Connection Status ════" -ForegroundColor Cyan
        Write-Host "User ID: $UserId" -ForegroundColor Green
        Write-Host "API: $ApiUrl" -ForegroundColor Green
        Write-Host "Messages Sent: $MessageCount" -ForegroundColor Green
        $Uptime = (Get-Date) - $SessionStart
        Write-Host "Session Uptime: $($Uptime.ToString('hh\:mm\:ss'))" -ForegroundColor Green
        Write-Host ""
    }
    elseif ($UserInput -eq "/history") {
        Write-Host ""
        Write-Host "[INFO] Fetching conversation history..." -ForegroundColor Yellow
        try {
            $Response = Invoke-WebRequest -Uri $HistoryEndpoint -Method Get -TimeoutSec 10 -ErrorAction Stop
            $Data = $Response.Content | ConvertFrom-Json
            
            if ($Data.messages -and $Data.messages.Count -gt 0) {
                Write-Host "════ Conversation History ════" -ForegroundColor Cyan
                foreach ($Msg in $Data.messages) {
                    if ($Msg.role -eq 'user') {
                        Write-Host "You: $($Msg.content)" -ForegroundColor Green
                    } else {
                        Write-Host "SOTA: $($Msg.content)" -ForegroundColor Magenta
                    }
                }
            } else {
                Write-Host "[INFO] No conversation history yet" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[ERROR] Could not fetch history: $($_.Exception.Message)" -ForegroundColor Red
        }
        Write-Host ""
    }
    else {
        # Send message to SOTA
        Write-Host ""
        Write-Host "You: $UserInput" -ForegroundColor Green
        
        try {
            Write-Host "[INFO] Sending to SOTA..." -ForegroundColor Yellow
            
            $Body = @{
                user_id = $UserId
                message = $UserInput
            } | ConvertTo-Json
            
            $Response = Invoke-WebRequest `
                -Uri $ChatEndpoint `
                -Method Post `
                -Headers @{'Content-Type' = 'application/json'} `
                -Body $Body `
                -TimeoutSec 30 `
                -ErrorAction Stop
            
            $Data = $Response.Content | ConvertFrom-Json
            
            if ($Data.response) {
                Write-Host "SOTA: $($Data.response)" -ForegroundColor Magenta
                $MessageCount++
            } else {
                Write-Host "[ERROR] Empty response from SOTA" -ForegroundColor Red
            }
        } catch {
            Write-Host "[ERROR] Failed to send message: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        Write-Host ""
    }
}
