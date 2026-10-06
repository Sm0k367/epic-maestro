@echo off
REM Epic Maestro SOTA - Start Script
REM Starts the SOTA chat system with all dependencies

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  ^:^) Epic Maestro SOTA - Startup Script
echo ========================================
echo.

REM Get the script directory
set "scriptDir=%~dp0"
echo Folder: %scriptDir%
echo.

REM Check if docker-compose.yml exists
if not exist "%scriptDir%docker-compose.yml" (
    echo ERROR: docker-compose.yml not found in %scriptDir%
    echo Make sure you run this script from the epic-maestro folder
    pause
    exit /b 1
)

echo Found: docker-compose.yml
echo.

REM Menu
echo Select an option:
echo 1. Start all containers
echo 2. Stop all containers
echo 3. Restart Maestro ^(full rebuild^)
echo 4. View logs
echo 5. Check container status
echo 6. Open SOTA in browser
echo 7. Exit
echo.

set /p choice="Enter choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Starting all containers...
    call docker-compose up -d
    timeout /t 5 /nobreak
    echo.
    echo OK: Containers started!
    echo SOTA UI: http://localhost:8800/chat
    echo Swagger API: http://localhost:8800/docs
    pause
)
else if "%choice%"=="2" (
    echo.
    echo Stopping all containers...
    call docker-compose down
    echo.
    echo OK: Containers stopped!
    pause
)
else if "%choice%"=="3" (
    echo.
    echo Full rebuild ^(stopping, removing, rebuilding^)...
    call docker-compose down
    call docker rmi epic-maestro-maestro:latest -f >nul 2>&1
    call docker system prune -f >nul 2>&1
    call docker-compose up -d
    timeout /t 10 /nobreak
    echo.
    echo OK: Rebuild complete!
    echo SOTA UI: http://localhost:8800/chat
    pause
)
else if "%choice%"=="4" (
    echo.
    echo Maestro Container Logs ^(last 30 lines^):
    call docker logs epic-maestro-master --tail 30
    pause
)
else if "%choice%"=="5" (
    echo.
    echo Container Status:
    call docker ps -a --filter "name=epic" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    pause
)
else if "%choice%"=="6" (
    echo.
    echo Opening SOTA in browser...
    start http://localhost:8800/chat
    echo OK: Browser opened!
    pause
)
else if "%choice%"=="7" (
    echo.
    echo Goodbye!
    exit /b 0
)
else (
    echo.
    echo ERROR: Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
echo ========================================
echo For more options, run this script again
echo ========================================
pause
