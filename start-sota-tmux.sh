#!/bin/bash
# Epic Maestro SOTA - Tmux Session Manager
# Organizes all SOTA components in a single tmux session with multiple panes

set -e

SESSION="SOTA"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🚀 Epic Maestro SOTA - Tmux Session${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Kill existing session if it exists
if tmux has-session -t $SESSION 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Session '$SESSION' already exists. Killing...${NC}"
    tmux kill-session -t $SESSION
    sleep 1
fi

echo -e "${CYAN}Creating tmux session: $SESSION${NC}"

# Create main session with first window
tmux new-session -d -s $SESSION -x 200 -y 50

# Window 1: Docker Compose (Main)
tmux rename-window -t $SESSION:0 "Docker"
tmux send-keys -t $SESSION:Docker "cd '$REPO_DIR' && clear && echo '📦 Docker Compose - Epic Maestro' && docker-compose logs -f" Enter
echo -e "${GREEN}✓ Window 'Docker' created - showing docker-compose logs${NC}"

# Window 2: Maestro API Status
tmux new-window -t $SESSION -n "Maestro"
tmux send-keys -t $SESSION:Maestro "cd '$REPO_DIR' && sleep 10 && clear && echo '🎭 Maestro API Status' && while true; do echo '---'; curl -s http://localhost:8800/docs >/dev/null && echo '✓ API is UP' || echo '✗ API is DOWN'; sleep 5; done" Enter
echo -e "${GREEN}✓ Window 'Maestro' created - monitoring API health${NC}"

# Window 3: SOTA Chat Status
tmux new-window -t $SESSION -n "SOTA"
tmux send-keys -t $SESSION:SOTA "cd '$REPO_DIR' && sleep 15 && clear && echo '💬 SOTA Chat Agent Status' && while true; do echo '---'; curl -s http://localhost:8800/api/chat -X POST -H 'Content-Type: application/json' -d '{\"user_id\":\"monitor\",\"message\":\"status\"}' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo 'Waiting for SOTA...'; sleep 10; done" Enter
echo -e "${GREEN}✓ Window 'SOTA' created - monitoring chat endpoint${NC}"

# Window 4: Container Stats
tmux new-window -t $SESSION -n "Stats"
tmux send-keys -t $SESSION:Stats "cd '$REPO_DIR' && clear && echo '📊 Container Resource Usage' && watch -n 2 'docker stats --no-stream --format \"table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\" | grep epic'" Enter
echo -e "${GREEN}✓ Window 'Stats' created - showing CPU/Memory usage${NC}"

# Window 5: Interactive Shell
tmux new-window -t $SESSION -n "Shell"
tmux send-keys -t $SESSION:Shell "cd '$REPO_DIR' && clear && echo '🔧 Interactive Shell - Epic Maestro Directory' && bash" Enter
echo -e "${GREEN}✓ Window 'Shell' created - ready for manual commands${NC}"

# Window 6: Browser (if available)
tmux new-window -t $SESSION -n "Browser"
tmux send-keys -t $SESSION:Browser "clear && echo '🌐 Opening SOTA Web UI...' && sleep 2 && echo 'SOTA Chat: http://localhost:8800/chat' && echo 'API Docs: http://localhost:8800/docs' && sleep 2 && if command -v xdg-open &> /dev/null; then xdg-open http://localhost:8800/chat; elif command -v open &> /dev/null; then open http://localhost:8800/chat; else echo 'Manual: Open http://localhost:8800/chat in your browser'; fi && bash" Enter
echo -e "${GREEN}✓ Window 'Browser' created${NC}"

# Select first window (Docker logs)
tmux select-window -t $SESSION:Docker

echo ""
echo -e "${GREEN}✓ Tmux session created successfully!${NC}"
echo ""
echo -e "${CYAN}📋 Session Layout:${NC}"
echo "  1. ${YELLOW}Docker${NC}   - docker-compose logs (live)"
echo "  2. ${YELLOW}Maestro${NC}  - API health check (every 5s)"
echo "  3. ${YELLOW}SOTA${NC}    - Chat endpoint status (every 10s)"
echo "  4. ${YELLOW}Stats${NC}   - Container CPU/Memory (live)"
echo "  5. ${YELLOW}Shell${NC}   - Interactive bash shell"
echo "  6. ${YELLOW}Browser${NC} - Web UI links"
echo ""
echo -e "${CYAN}🎮 Tmux Shortcuts:${NC}"
echo "  Ctrl+B n  - Next window"
echo "  Ctrl+B p  - Previous window"
echo "  Ctrl+B 0-6 - Jump to window (0=Docker, 1=Maestro, etc.)"
echo "  Ctrl+B %  - Split pane vertically"
echo "  Ctrl+B \"  - Split pane horizontally"
echo "  Ctrl+B x  - Close pane"
echo "  Ctrl+B d  - Detach session (leaves it running)"
echo "  Ctrl+B [  - Enter scroll mode (q to exit)"
echo ""
echo -e "${CYAN}📱 To Reconnect:${NC}"
echo "  ${YELLOW}tmux attach -t $SESSION${NC}"
echo ""
echo -e "${CYAN}🌐 Quick Links:${NC}"
echo "  SOTA Chat UI: http://localhost:8800/chat"
echo "  API Docs: http://localhost:8800/docs"
echo "  Swagger UI: http://localhost:8800/docs"
echo ""

# Attach to session
echo -e "${GREEN}Attaching to session...${NC}"
sleep 1
tmux attach-session -t $SESSION
