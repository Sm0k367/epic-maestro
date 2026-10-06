# ============================================================================
# SOTA Chat CLI - WebSocket Version (Real-Time Streaming)
# ============================================================================
# Advanced interactive PowerShell chat client using WebSocket for 
# real-time streaming responses from SOTA.
#
# Note: This version requires .NET Framework 4.5+ and WebSocket support
# For simpler usage without streaming, use SOTA-Chat-CLI.ps1 instead
#
# Usage: .\SOTA-Chat-CLI-WebSocket.ps1
# ============================================================================

param(
    [string]$ApiUrl = "http://localhost:8800",
    [string]$UserId = "powershell-$(Get-Random -Maximum 9999)"
)

# ============================================================================
# Configuration
# ============================================================================

$Script:Config = @{
    BaseUrl       = $ApiUrl
    WsUrl         = $ApiUrl -replace 'http', 'ws'
    UserId        = $UserId
    ConnectTimeout = 10
}

$Script:State = @{
    Connected      = $false
    WebSocket      = $null
    SessionStart   = Get-Date
    MessageCount   = 0
}

$Script:Colors = @{
    Header       = 'Cyan'
    UserMessage  = 'Green'
    SOTAMessage  = 'Magenta'
    Status       = 'Yellow'
    Error        = 'Red'
    Success      = 'Green'
    Info         = 'Cyan'
}

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = 'Info')
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch($Type) {
        'Success' { $Script:Colors.Success }
        'Error'   { $Script:Colors.Error }
        'Warning' { $Script:Colors.Status }
        default   { $Script:Colors.Info }
    }
    
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

function Connect-WebSocket {
    try {
        Write-Status "Connecting to SOTA WebSocket..." -Type Info
        
        $wsUrl = "$($Script:Config.WsUrl)/ws/chat/$($Script:Config.UserId)"
        Write-Status "WebSocket URL: $wsUrl" -Type Info
        
        # Create WebSocket client
        Add-Type -AssemblyName System.Net.WebSockets.Client
        
        $Script:State.WebSocket = New-Object System.Net.WebSockets.ClientWebSocket
        $ct = New-Object System.Threading.CancellationToken($false)
        
        # Connect
        $Script:State.WebSocket.ConnectAsync($wsUrl, $ct).Wait($Script:Config.ConnectTimeout * 1000) | Out-Null
        
        if ($Script:State.WebSocket.State -eq 'Open') {
            Write-Status "✓ Connected to SOTA WebSocket" -Type Success
            $Script:State.Connected = $true
            return $true
        } else {
            Write-Status "✗ WebSocket connection failed" -Type Error
            return $false
        }
    } catch {
        Write-Status "Error: $($_.Exception.Message)" -Type Error
        return $false
    }
}

function Send-WebSocketMessage {
    param([string]$Message)
    
    if ($Script:State.WebSocket.State -ne 'Open') {
        Write-Status "WebSocket not connected" -Type Error
        return $false
    }
    
    try {
        $json = @{type = "message"; content = $Message} | ConvertTo-Json
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $ct = New-Object System.Threading.CancellationToken($false)
        
        $Script:State.WebSocket.SendAsync(
            [System.ArraySegment[byte]]$bytes,
            [System.Net.WebSockets.WebSocketMessageType]::Text,
            $true,
            $ct
        ).Wait() | Out-Null
        
        return $true
    } catch {
        Write-Status "Error sending message: $($_.Exception.Message)" -Type Error
        return $false
    }
}

function Receive-WebSocketMessage {
    try {
        $buffer = New-Object byte[] 4096
        $ct = New-Object System.Threading.CancellationToken($false)
        
        $result = $Script:State.WebSocket.ReceiveAsync(
            [System.ArraySegment[byte]]$buffer,
            $ct
        ).Result
        
        if ($result.MessageType -eq 'Text' -and $result.Count -gt 0) {
            $json = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
            $data = $json | ConvertFrom-Json
            return $data.content
        }
    } catch {
        # Connection might be closed
        return $null
    }
}

function Display-UserMessage {
    param([string]$Message)
    Write-Host ""
    Write-Host "┌─ You" -ForegroundColor $Script:Colors.UserMessage
    Write-Host "│ $Message" -ForegroundColor $Script:Colors.UserMessage
    Write-Host "└─" -ForegroundColor $Script:Colors.UserMessage
}

function Display-SOTAMessage {
    param([string]$Message)
    Write-Host ""
    Write-Host "┌─ SOTA" -ForegroundColor $Script:Colors.SOTAMessage
    Write-Host "│ $Message" -ForegroundColor $Script:Colors.SOTAMessage
    Write-Host "└─" -ForegroundColor $Script:Colors.SOTAMessage
}

function Show-Header {
    Write-Host "`n" -NoNewline
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $Script:Colors.Header
    Write-Host "║         SOTA Chat CLI - WebSocket Real-Time Version          ║" -ForegroundColor $Script:Colors.Header
    Write-Host "║            State-of-the-Art Orchestration Agent              ║" -ForegroundColor $Script:Colors.Header
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $Script:Colors.Header
    Write-Host ""
}

# ============================================================================
# Main Chat Loop
# ============================================================================

Show-Header

$ProgressPreference = 'SilentlyContinue'

Write-Status "User ID: $($Script:Config.UserId)" -Type Info
Write-Status "Base URL: $($Script:Config.BaseUrl)" -Type Info
Write-Host ""

if (-not (Connect-WebSocket)) {
    Write-Status "Failed to connect. Exiting." -Type Error
    exit 1
}

Write-Status "Type 'exit' to quit" -Type Success
Write-Host ""

while ($Script:State.Connected) {
    Write-Host ""
    Write-Host "You > " -ForegroundColor $Script:Colors.Header -NoNewline
    $input = Read-Host
    
    if ($input -eq 'exit') {
        break
    }
    
    if (-not $input) {
        continue
    }
    
    Display-UserMessage $input
    
    if (Send-WebSocketMessage $input) {
        $response = Receive-WebSocketMessage
        if ($response) {
            Display-SOTAMessage $response
            $Script:State.MessageCount++
        }
    }
}

Write-Host ""
Write-Status "Disconnecting..." -Type Info
$Script:State.WebSocket.Close()

$uptime = (Get-Date) - $Script:State.SessionStart
Write-Status "Session duration: $($uptime.ToString('hh\:mm\:ss'))" -Type Info
Write-Status "Messages sent: $($Script:State.MessageCount)" -Type Info
Write-Host ""
