# Epic Maestro SOTA - Start Script
# Starts the SOTA chat system with all dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Epic Maestro SOTA - Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "📁 Working directory: $scriptDir" -ForegroundColor Yellow

# Check if docker-compose.yml exists
if (-not (Test-Path "$scriptDir/docker-compose.yml")) {
    Write-Host "❌ Error: docker-compose.yml not found in $scriptDir" -ForegroundColor Red
    Write-Host "Make sure you run this script from the epic-maestro folder" -ForegroundColor Red
    exit 1
}

Write-Host "✓ docker-compose.yml found" -ForegroundColor Green
Write-Host ""

# Menu
Write-Host "Select an option:" -ForegroundColor Cyan
Write-Host "1. Start all containers" -ForegroundColor White
Write-Host "2. Stop all containers" -ForegroundColor White
Write-Host "3. Restart Maestro (full rebuild)" -ForegroundColor White
Write-Host "4. View logs" -ForegroundColor White
Write-Host "5. Check container status" -ForegroundColor White
Write-Host "6. Open SOTA in browser (http://localhost:8800/chat)" -ForegroundColor White
Write-Host "7. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-7)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting all containers..." -ForegroundColor Cyan
        docker-compose up -d
        Start-Sleep -Seconds 5
        Write-Host ""
        Write-Host "✓ Containers started!" -ForegroundColor Green
        Write-Host "🌐 SOTA UI: http://localhost:8800/chat" -ForegroundColor Green
        Write-Host "📊 Swagger API: http://localhost:8800/docs" -ForegroundColor Green
    }
    
    "2" {
        Write-Host ""
        Write-Host "⏹️  Stopping all containers..." -ForegroundColor Cyan
        docker-compose down
        Write-Host ""
        Write-Host "✓ Containers stopped!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host ""
        Write-Host "🔄 Full rebuild (stopping, removing old image, rebuilding)..." -ForegroundColor Cyan
        docker-compose down
        docker rmi epic-maestro-maestro:latest -f 2>$null
        docker system prune -f 2>$null
        docker-compose up -d
        Start-Sleep -Seconds 10
        Write-Host ""
        Write-Host "✓ Rebuild complete!" -ForegroundColor Green
        Write-Host "🌐 SOTA UI: http://localhost:8800/chat" -ForegroundColor Green
    }
    
    "4" {
        Write-Host ""
        Write-Host "📋 Maestro Container Logs (last 30 lines):" -ForegroundColor Cyan
        docker logs epic-maestro-master --tail 30
    }
    
    "5" {
        Write-Host ""
        Write-Host "📊 Container Status:" -ForegroundColor Cyan
        docker ps -a --filter "name=epic" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    }
    
    "6" {
        Write-Host ""
        Write-Host "🌐 Opening SOTA in browser..." -ForegroundColor Cyan
        Start-Process "http://localhost:8800/chat"
        Write-Host "✓ Browser opened!" -ForegroundColor Green
    }
    
    "7" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "For more options, run this script again" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
