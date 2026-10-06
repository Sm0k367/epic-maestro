"""
SOTA Chat Web Interface
FastAPI + WebSocket for real-time conversational orchestration
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
from typing import Dict, Set
import uuid

from core.chat_agent import sota_agent, chat_with_sota

chat_app = FastAPI(title="SOTA Chat Interface", version="1.0")

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@chat_app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serve the chat web interface"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SOTA - State-of-the-Art Orchestration Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 900px;
            height: 90vh;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 28px; }
        .header .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ade80;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            display: flex;
            gap: 10px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { justify-content: flex-end; }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 10px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 0;
        }
        .message.assistant .message-content {
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 0;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-area input:focus { border-color: #667eea; }
        .input-area button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }
        .input-area button:hover { background: #764ba2; }
        .input-area button:active { transform: scale(0.95); }
        .thinking {
            display: flex;
            gap: 4px;
            align-items: center;
        }
        .thinking span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: thinking 1.4s infinite;
        }
        .thinking span:nth-child(2) { animation-delay: 0.2s; }
        .thinking span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes thinking {
            0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
            30% { opacity: 1; transform: translateY(-10px); }
        }
        .action-badge {
            display: inline-block;
            background: #e0e7ff;
            color: #667eea;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 8px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🚀 SOTA</h1>
                <p>State-of-the-Art Orchestration Agent</p>
            </div>
            <div class="status">
                <div class="status-dot"></div>
                <span>Maestro Connected</span>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages"></div>
            
            <div class="input-area">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Ask me to infer, stitch, broadcast, check status, learn patterns... anything!" 
                    autocomplete="off"
                />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const userId = 'web-' + Math.random().toString(36).substr(2, 9);
        let ws = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws/chat/' + userId);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                displayMessage(data.content, data.role, data.action);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addSystemMessage('Connection error. Please refresh.');
            };
        }

        function displayMessage(content, role, action = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;
            
            let html = '<div class="message-content">' + escapeHtml(content);
            if (action) {
                html += '<br><span class="action-badge">🔧 ' + action + '</span>';
            }
            html += '</div>';
            
            messageDiv.innerHTML = html;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function showThinking() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.innerHTML = '<div class="message-content"><div class="thinking"><span></span><span></span><span></span></div></div>';
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return messageDiv;
        }

        function addSystemMessage(text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.innerHTML = '<div class="message-content" style="font-style: italic; color: #999;">' + text + '</div>';
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            messageInput.value = '';
            displayMessage(message, 'user');
            showThinking();
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'message', content: message }));
            }
        }

        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Initial setup
        addSystemMessage('SOTA Connected! Ask me anything about orchestration, inference, stitching, broadcasting, or system health.');
        connectWebSocket();
    </script>
</body>
</html>
"""

@chat_app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'message':
                # Get response from SOTA agent
                response = await chat_with_sota(user_id, message_data['content'])
                
                # Send back response
                await websocket.send_text(json.stringify({
                    'role': 'assistant',
                    'content': response,
                    'action': 'Orchestrating...'
                }))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        del active_connections[user_id]

def json.stringify(obj):
    return json.dumps(obj)

# Mount chat interface alongside Maestro API
def setup_chat_routes(maestro_app):
    """Mount chat routes to existing Maestro app"""
    
    @maestro_app.get("/chat", response_class=HTMLResponse)
    async def get_chat():
        return await get_chat_ui()
    
    @maestro_app.websocket("/ws/chat/{user_id}")
    async def ws_chat(websocket: WebSocket, user_id: str):
        await websocket_chat(websocket, user_id)
    
    @maestro_app.post("/api/chat")
    async def api_chat(user_id: str, message: str):
        """REST API for chat (for non-WebSocket clients)"""
        response = await chat_with_sota(user_id, message)
        return {'user_id': user_id, 'response': response}
    
    @maestro_app.get("/api/chat/history/{user_id}")
    async def get_history(user_id: str):
        """Get conversation history"""
        return sota_agent.get_conversation_history(user_id)

