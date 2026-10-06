#!/usr/bin/env python3
"""
SOTA Chat CLI - Interactive Command-Line Chat Client
State-of-the-Art Orchestration Agent - Real-time Terminal Interface

Usage:
    python3 SOTA-Chat-CLI.py                    # Use defaults (localhost:8800)
    python3 SOTA-Chat-CLI.py --api http://10.0.0.5:8800
    python3 SOTA-Chat-CLI.py --user my-session

Features:
    - Real-time chat with SOTA in your terminal
    - Conversation history tracking
    - Color-coded messages
    - Session management
    - Multiple commands for system control
"""

import sys
import json
import requests
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print welcome header"""
    print(f"\n{Colors.CYAN}{'='*66}{Colors.RESET}")
    print(f"{Colors.CYAN}║  {Colors.BOLD}SOTA Chat CLI - Interactive Terminal Interface{Colors.RESET}{Colors.CYAN}     ║{Colors.RESET}")
    print(f"{Colors.CYAN}║  {Colors.BOLD}State-of-the-Art Orchestration Agent{Colors.RESET}{Colors.CYAN}              ║{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*66}{Colors.RESET}\n")

def print_status(message: str, status_type: str = "info"):
    """Print colored status messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if status_type == "success":
        symbol = "✓"
        color = Colors.GREEN
    elif status_type == "error":
        symbol = "✗"
        color = Colors.RED
    elif status_type == "warning":
        symbol = "⚠"
        color = Colors.YELLOW
    elif status_type == "busy":
        symbol = "⟳"
        color = Colors.YELLOW
    else:
        symbol = "ℹ"
        color = Colors.CYAN
    
    print(f"{color}[{timestamp}] {symbol} {message}{Colors.RESET}")

def print_help():
    """Print help information"""
    print(f"\n{Colors.CYAN}{'='*66}{Colors.RESET}")
    print(f"{Colors.CYAN}Available Commands{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*66}{Colors.RESET}\n")
    
    commands = [
        ("/help", "Show this help message"),
        ("/clear", "Clear the screen"),
        ("/status", "Show connection status"),
        ("/history", "Show conversation history"),
        ("/exit", "Exit the chat"),
        ("", ""),
        ("Example Queries:", ""),
        ("  • System health", "Check infrastructure status"),
        ("  • Infer best approach", "Get reasoning about tasks"),
        ("  • Stitch video files", "Process video stitching"),
        ("  • Broadcast to workers", "Distribute work"),
        ("  • Learn patterns", "Train on workflows"),
        ("  • Detect failures", "Check for issues"),
        ("  • Improve performance", "Optimize system"),
    ]
    
    for cmd, desc in commands:
        if cmd == "":
            print()
        elif desc == "":
            print(f"{Colors.BOLD}{Colors.YELLOW}{cmd}{Colors.RESET}")
        else:
            print(f"  {Colors.GREEN}{cmd:<25}{Colors.RESET} {desc}")
    
    print()

def test_connection(api_url: str) -> bool:
    """Test connection to SOTA API"""
    print_status("Testing connection to SOTA API...", "busy")
    
    try:
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code == 200:
            print_status(f"Connected to SOTA API at {api_url}", "success")
            return True
    except Exception as e:
        print_status(f"Failed to connect to SOTA API at {api_url}", "error")
        print_status(f"Error: {str(e)}", "error")
        print_status("Make sure SOTA is running: docker-compose up -d", "info")
        return False

def send_message(api_url: str, user_id: str, message: str) -> Optional[str]:
    """Send message to SOTA API and get response"""
    try:
        endpoint = f"{api_url}/api/chat"
        payload = {
            "user_id": user_id,
            "message": message
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response")
        else:
            return None
            
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
        return None

def get_history(api_url: str, user_id: str) -> Optional[list]:
    """Retrieve conversation history"""
    try:
        endpoint = f"{api_url}/api/chat/history/{user_id}"
        response = requests.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
    except Exception as e:
        print_status(f"Could not fetch history: {str(e)}", "warning")
    
    return None

def display_user_message(message: str):
    """Display user message in terminal"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.GREEN}┌─ You [{timestamp}]{Colors.RESET}")
    print(f"{Colors.GREEN}│ {message}{Colors.RESET}")
    print(f"{Colors.GREEN}└─{Colors.RESET}\n")

def display_sota_message(message: str):
    """Display SOTA response in terminal"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.MAGENTA}┌─ SOTA [{timestamp}]{Colors.RESET}")
    
    # Word wrap long responses
    words = message.split()
    line = ""
    max_length = 70
    
    for word in words:
        if len(line) + len(word) + 1 > max_length:
            print(f"{Colors.MAGENTA}│ {line}{Colors.RESET}")
            line = word
        else:
            line += (" " + word) if line else word
    
    if line:
        print(f"{Colors.MAGENTA}│ {line}{Colors.RESET}")
    
    print(f"{Colors.MAGENTA}└─{Colors.RESET}\n")

def main():
    """Main chat loop"""
    parser = argparse.ArgumentParser(
        description="SOTA Chat CLI - Interactive chat with State-of-the-Art Orchestration Agent"
    )
    parser.add_argument(
        "--api",
        default="http://localhost:8800",
        help="SOTA API URL (default: http://localhost:8800)"
    )
    parser.add_argument(
        "--user",
        default=f"cli-user-{datetime.now().timestamp()}",
        help="Session user ID for history tracking"
    )
    
    args = parser.parse_args()
    api_url = args.api
    user_id = args.user
    
    # Print header
    print_header()
    
    print_status(f"Session ID: {user_id}", "info")
    print_status(f"API URL: {api_url}", "info")
    print()
    
    # Test connection
    if not test_connection(api_url):
        sys.exit(1)
    
    print_status("Type '/help' for commands or start chatting!", "success")
    print()
    
    message_count = 0
    session_start = datetime.now()
    
    # Main chat loop
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.GREEN}You > {Colors.RESET}").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input == "/exit":
                print()
                print_status("Thank you for using SOTA Chat CLI!", "success")
                uptime = datetime.now() - session_start
                print_status(f"Session duration: {str(uptime).split('.')[0]}", "info")
                print_status(f"Messages sent: {message_count}", "info")
                print()
                break
            
            elif user_input == "/help":
                print_help()
            
            elif user_input == "/clear":
                print("\033[2J\033[H", end="")  # Clear screen
                print_header()
            
            elif user_input == "/status":
                print()
                print_status(f"User ID: {user_id}", "info")
                print_status(f"API: {api_url}", "info")
                print_status(f"Messages Sent: {message_count}", "info")
                uptime = datetime.now() - session_start
                print_status(f"Session Uptime: {str(uptime).split('.')[0]}", "info")
                print()
            
            elif user_input == "/history":
                print()
                print_status("Fetching conversation history...", "busy")
                history = get_history(api_url, user_id)
                
                if history and len(history) > 0:
                    print(f"\n{Colors.CYAN}{'='*66}{Colors.RESET}")
                    print(f"{Colors.CYAN}Conversation History{Colors.RESET}")
                    print(f"{Colors.CYAN}{'='*66}{Colors.RESET}\n")
                    
                    for msg in history:
                        if msg.get("role") == "user":
                            print(f"{Colors.GREEN}You: {msg.get('content')}{Colors.RESET}")
                        else:
                            print(f"{Colors.MAGENTA}SOTA: {msg.get('content')}{Colors.RESET}")
                    print()
                else:
                    print_status("No conversation history yet", "warning")
                    print()
            
            else:
                # Send message to SOTA
                display_user_message(user_input)
                print_status("Sending to SOTA...", "busy")
                
                response = send_message(api_url, user_id, user_input)
                
                if response:
                    display_sota_message(response)
                    message_count += 1
                else:
                    print_status("Failed to get response from SOTA", "error")
                    print()
        
        except KeyboardInterrupt:
            print()
            print_status("Chat interrupted by user", "info")
            break
        except Exception as e:
            print_status(f"Error: {str(e)}", "error")

if __name__ == "__main__":
    main()
