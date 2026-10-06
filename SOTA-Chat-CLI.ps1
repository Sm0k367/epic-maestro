# ============================================================================
# SOTA Chat CLI - Interactive PowerShell Chat Client
# ============================================================================
# A real-time interactive chat interface for SOTA (State-of-the-Art 
# Orchestration Agent) running in your PowerShell terminal.
# 
# Usage: .\SOTA-Chat-CLI.ps1
# Features:
#   - Real-time chat with SOTA AI agent
#   - Conversation history tracking
#   - Color-coded messages (user vs SOTA)
#   - Status indicators
#   - Clear/help commands
#   - Exit gracefully
#
# Requirements:
#   - PowerShell 5.0+ (or PowerShell Core on Linux/Mac)
#   - SOTA API running (default: http://localhost:8800)
#   - Internet connectivity to reach SOTA server
# ============================================================================

param(
    [string]$ApiUrl = "http://localhost:8800",
    [string]$UserId = "powershell-$(Get-Random -Maximum 9999)"
)

# ============================================================================
# Configuration
# ============================================================================

$Script:Config = @{
    ApiUrl        = $ApiUrl
    UserId        = $UserId
    ChatEndpoint  = "$ApiUrl/api/chat"
    HistoryEndpoint = "$ApiUrl/api/chat/history/$UserId"
    ConnectTimeout = 5
    ReadTimeout   = 30
    Retries       = 3
}

$Script:State = @{
    Connected      = $false
    MessageCount   = 0
    SessionStart   = Get-Date
    ConversationId = "session-$(Get-Random -Maximum 9999)"
}

# ============================================================================
# Color Themes
# ============================================================================

$Script:Colors = @{
    Header       = 'Cyan'
    UserMessage  = 'Green'
    SOTAMessage  = 'Magenta'
    Status       = 'Yellow'
    Error        = 'Red'
    Success      = 'Green'
    Info         = 'Cyan'
    InputPrompt  = 'White'
    Separator    = 'DarkGray'
}

# ============================================================================
# Helper Functions
# ============================================================================

function Write-ColoredText {
    param(
        [string]$Text,
        [string]$Color = 'White'
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    Write-Host "`n" -NoNewline
    Write-ColoredText "╔════════════════════════════════════════════════════════════════╗" $Colors.Separator
    Write-ColoredText "║                    SOTA Chat CLI - Interactive                ║" $Colors.Header
    Write-ColoredText "║            State-of-the-Art Orchestration Agent              ║" $Colors.Info
    Write-ColoredText "╚════════════════════════════════════════════════════════════════╝" $Colors.Separator
    Write-Host ""
}

function Write-Status {
    param([string]$Message, [string]$Type = 'Info')
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $icon = switch($Type) {
        'Success' { '✓' }
        'Error'   { '✗' }
        'Info'    { 'ℹ' }
        'Warning' { '⚠' }
        'Busy'    { '⟳' }
        default   { '◆' }
    }
    
    $color = switch($Type) {
        'Success' { $Colors.Success }
        'Error'   { $Colors.Error }
        'Warning' { $Colors.Status }
        'Busy'    { $Colors.Status }
        default   { $Colors.Info }
    }
    
    Write-ColoredText "[$timestamp] $icon $Message" $color
}

function Test-SOTAConnection {
    try {
        Write-Status "Testing connection to SOTA API..." Busy
        
        $response = Invoke-WebRequest `
            -Uri "$($Script:Config.ApiUrl)/docs" `
            -Method Get `
            -TimeoutSec $Script:Config.ConnectTimeout `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Status "Connected to SOTA API at $($Script:Config.ApiUrl)" Success
            $Script:State.Connected = $true
            return $true
        }
    } catch {
        Write-Status "Failed to connect to SOTA API at $($Script:Config.ApiUrl)" Error
        Write-Status "Error: $($_.Exception.Message)" Error
        Write-Status "Make sure SOTA is running: docker-compose up -d" Info
        return $false
    }
}

function Send-Message {
    param([string]$Message)
    
    if (-not $Script:State.Connected) {
        Write-Status "Not connected to SOTA. Reconnecting..." Warning
        if (-not (Test-SOTAConnection)) {
            return $null
        }
    }
    
    try {
        # Build request body
        $body = @{
            user_id = $Script:Config.UserId
            message = $Message
        } | ConvertTo-Json
        
        Write-Status "Sending message to SOTA..." Busy
        
        # Send to SOTA API
        $response = Invoke-WebRequest `
            -Uri $Script:Config.ChatEndpoint `
            -Method Post `
            -Headers @{'Content-Type' = 'application/json'} `
            -Body $body `
            -TimeoutSec $Script:Config.ReadTimeout `
            -ErrorAction Stop
        
        # Parse response
        $data = $response.Content | ConvertFrom-Json
        
        if ($data.response) {
            $Script:State.MessageCount++
            return $data.response
        } else {
            Write-Status "Empty response from SOTA" Warning
            return "No response received."
        }
        
    } catch {
        Write-Status "Error communicating with SOTA API" Error
        Write-Status "Details: $($_.Exception.Message)" Error
        
        # Retry logic
        if ($Script:Config.Retries -gt 0) {
            $Script:Config.Retries--
            Write-Status "Retrying... ($($Script:Config.Retries) attempts left)" Warning
            Start-Sleep -Seconds 1
            return Send-Message $Message
        }
        
        return $null
    }
}

function Display-UserMessage {
    param([string]$Message)
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host ""
    Write-ColoredText "┌─ You [$timestamp]" $Colors.UserMessage
    Write-Host "│ $Message" -ForegroundColor $Colors.UserMessage
    Write-ColoredText "└─" $Colors.UserMessage
}

function Display-SOTAMessage {
    param([string]$Message)
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host ""
    Write-ColoredText "┌─ SOTA [$timestamp]" $Colors.SOTAMessage
    
    # Word wrap for long responses
    $words = $Message -split ' '
    $line = ""
    $maxLength = 70
    
    foreach ($word in $words) {
        if (($line + " " + $word).Length -gt $maxLength) {
            Write-Host "│ $line" -ForegroundColor $Colors.SOTAMessage
            $line = $word
        } else {
            $line += " $word"
        }
    }
    
    if ($line) {
        Write-Host "│ $line" -ForegroundColor $Colors.SOTAMessage
    }
    
    Write-ColoredText "└─" $Colors.SOTAMessage
}

function Show-Help {
    Write-Host ""
    Write-ColoredText "╔════════════════════════════════════════════════════════════════╗" $Colors.Separator
    Write-ColoredText "║                           Commands                            ║" $Colors.Header
    Write-ColoredText "╚════════════════════════════════════════════════════════════════╝" $Colors.Separator
    Write-Host ""
    
    $commands = @(
        @{Cmd = '/help'; Desc = 'Show this help message'; Icon = '?' },
        @{Cmd = '/clear'; Desc = 'Clear the screen'; Icon = '⟲' },
        @{Cmd = '/status'; Desc = 'Show connection status'; Icon = '◆' },
        @{Cmd = '/history'; Desc = 'Show conversation history'; Icon = '📋' },
        @{Cmd = '/exit'; Desc = 'Exit the chat'; Icon = '⊗' },
        @{Cmd = ''; Desc = ''; Icon = '' },
        @{Cmd = 'Example queries:'; Desc = ''; Icon = '' },
        @{Cmd = '  • System health'; Desc = 'Check infrastructure status'; Icon = '◆' },
        @{Cmd = '  • Infer best approach'; Desc = 'Get reasoning about tasks'; Icon = '◆' },
        @{Cmd = '  • Stitch video files'; Desc = 'Process video stitching'; Icon = '◆' },
        @{Cmd = '  • Broadcast to workers'; Desc = 'Distribute work'; Icon = '◆' },
        @{Cmd = '  • Learn patterns'; Desc = 'Train on workflow patterns'; Icon = '◆' },
        @{Cmd = '  • Detect failures'; Desc = 'Check for issues'; Icon = '◆' },
        @{Cmd = '  • Improve performance'; Desc = 'Optimize system'; Icon = '◆' },
    )
    
    foreach ($item in $commands) {
        if ($item.Cmd -eq '') {
            Write-Host ""
        } else {
            $paddedCmd = $item.Cmd.PadRight(25)
            Write-ColoredText "$($item.Icon) $paddedCmd" $Colors.Status
            if ($item.Desc) {
                Write-Host "  $($item.Desc)" -ForegroundColor $Colors.Info
            }
        }
    }
    
    Write-Host ""
}

function Show-Status {
    $uptime = (Get-Date) - $Script:State.SessionStart
    $uptimeStr = "{0}h {1}m {2}s" -f $uptime.Hours, $uptime.Minutes, $uptime.Seconds
    
    Write-Host ""
    Write-ColoredText "╔════════════════════════════════════════════════════════════════╗" $Colors.Separator
    Write-ColoredText "║                       Connection Status                       ║" $Colors.Header
    Write-ColoredText "╚════════════════════════════════════════════════════════════════╝" $Colors.Separator
    Write-Host ""
    
    $statusSymbol = if ($Script:State.Connected) { "●" } else { "○" }
    $statusColor = if ($Script:State.Connected) { $Colors.Success } else { $Colors.Error }
    
    Write-Host "Status:              " -NoNewline
    Write-ColoredText "$statusSymbol Connected" $statusColor
    
    Write-Host "API Endpoint:        " -NoNewline
    Write-ColoredText $Script:Config.ApiUrl $Colors.Info
    
    Write-Host "Session ID:          " -NoNewline
    Write-ColoredText $Script:Config.UserId $Colors.Info
    
    Write-Host "Messages Sent:       " -NoNewline
    Write-ColoredText $Script:State.MessageCount $Colors.Info
    
    Write-Host "Session Uptime:      " -NoNewline
    Write-ColoredText $uptimeStr $Colors.Info
    
    Write-Host ""
}

function Get-ConversationHistory {
    try {
        Write-Status "Fetching conversation history..." Busy
        
        $response = Invoke-WebRequest `
            -Uri $Script:Config.HistoryEndpoint `
            -Method Get `
            -TimeoutSec $Script:Config.ConnectTimeout `
            -ErrorAction Stop
        
        $data = $response.Content | ConvertFrom-Json
        
        if ($data.messages -and $data.messages.Count -gt 0) {
            Write-Host ""
            Write-ColoredText "╔════════════════════════════════════════════════════════════════╗" $Colors.Separator
            Write-ColoredText "║                    Conversation History                       ║" $Colors.Header
            Write-ColoredText "╚════════════════════════════════════════════════════════════════╝" $Colors.Separator
            Write-Host ""
            
            foreach ($msg in $data.messages) {
                if ($msg.role -eq 'user') {
                    Display-UserMessage $msg.content
                } else {
                    Display-SOTAMessage $msg.content
                }
            }
            Write-Host ""
        } else {
            Write-Status "No conversation history yet" Info
        }
        
    } catch {
        Write-Status "Could not fetch conversation history" Warning
        Write-Status "Details: $($_.Exception.Message)" Error
    }
}

# ============================================================================
# Main Chat Loop
# ============================================================================

function Start-ChatLoop {
    Write-Header
    
    Write-Status "Session ID: $($Script:Config.UserId)" Info
    Write-Status "API URL: $($Script:Config.ApiUrl)" Info
    Write-Host ""
    
    # Test connection
    if (-not (Test-SOTAConnection)) {
        Write-Status "Failed to connect. Exiting." Error
        return
    }
    
    Write-Status "Type '/help' for commands or start chatting!" Success
    Write-Host ""
    
    # Main loop
    while ($true) {
        # Show input prompt
        Write-Host ""
        Write-ColoredText "You > " $Colors.InputPrompt -NoNewline
        
        # Read input
        $input = Read-Host
        $input = $input.Trim()
        
        if (-not $input) {
            continue
        }
        
        # Handle commands
        switch -Regex ($input) {
            '^/exit$' {
                Write-Host ""
                Write-Status "Thank you for using SOTA Chat CLI!" Success
                $uptime = (Get-Date) - $Script:State.SessionStart
                Write-Status "Session duration: $($uptime.ToString('hh\:mm\:ss'))" Info
                Write-Status "Messages sent: $($Script:State.MessageCount)" Info
                Write-Host ""
                exit 0
            }
            '^/help$' {
                Show-Help
            }
            '^/clear$' {
                Clear-Host
                Write-Header
            }
            '^/status$' {
                Show-Status
            }
            '^/history$' {
                Get-ConversationHistory
            }
            default {
                # Send message to SOTA
                Display-UserMessage $input
                
                $response = Send-Message $input
                
                if ($response) {
                    Display-SOTAMessage $response
                } else {
                    Write-Status "Failed to get response from SOTA" Error
                }
            }
        }
    }
}

# ============================================================================
# Entry Point
# ============================================================================

# Check if running as admin (optional, for better file access if needed)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

# Disable progress bar for cleaner output
$ProgressPreference = 'SilentlyContinue'

# Start the chat
try {
    Start-ChatLoop
} catch {
    Write-Status "Fatal error: $($_.Exception.Message)" Error
    Write-Status "Stack: $($_.ScriptStackTrace)" Error
    exit 1
}
