#!/usr/bin/env python3
import os
import json
from aiohttp import web
from orchestrator import orchestrator

# ALL 100+ SKILLS
SKILLS = {
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on/off flashlight", "phone": True},
    "flashlight_off": {"name": "🔦 Flashlight Off", "desc": "Turn off flashlight", "phone": True},
    "battery": {"name": "🔋 Battery", "desc": "Check battery status", "phone": True},
    "vibrate": {"name": "📳 Vibrate", "desc": "Make phone vibrate", "phone": True},
    "camera": {"name": "📷 Camera", "desc": "Take a photo", "phone": True},
    "screenshot": {"name": "📸 Screenshot", "desc": "Capture screen", "phone": True},
    "volume_up": {"name": "🔊 Volume Up", "desc": "Increase volume", "phone": True},
    "volume_down": {"name": "🔉 Volume Down", "desc": "Decrease volume", "phone": True},
    "wifi_on": {"name": "📶 WiFi On", "desc": "Turn on WiFi", "phone": True},
    "wifi_off": {"name": "📶 WiFi Off", "desc": "Turn off WiFi", "phone": True},
    "bluetooth_on": {"name": "📡 Bluetooth On", "desc": "Turn on Bluetooth", "phone": True},
    "bluetooth_off": {"name": "📡 Bluetooth Off", "desc": "Turn off Bluetooth", "phone": True},
    "location": {"name": "📍 Location", "desc": "Get GPS location", "phone": True},
    "weather": {"name": "🌤️ Weather", "desc": "Get weather forecast", "phone": False},
    "news": {"name": "📰 News", "desc": "Fetch latest news", "phone": False},
    "translate": {"name": "🌐 Translate", "desc": "Translate text", "phone": False},
    "email": {"name": "📧 Email", "desc": "Send email", "phone": False},
    "calendar": {"name": "📅 Calendar", "desc": "Manage events", "phone": False},
    "docx": {"name": "📄 Word", "desc": "Create Word document", "phone": False},
    "pdf": {"name": "📑 PDF", "desc": "Process PDF files", "phone": False},
    "telegram": {"name": "📱 Telegram", "desc": "Telegram bot", "phone": False},
    "whatsapp": {"name": "💬 WhatsApp", "desc": "WhatsApp messaging", "phone": False},
    "discord": {"name": "🎮 Discord", "desc": "Discord bot", "phone": False},
    "slack": {"name": "💼 Slack", "desc": "Slack workspace", "phone": False},
    "github": {"name": "🐙 GitHub", "desc": "GitHub integration", "phone": False},
    "docker": {"name": "🐳 Docker", "desc": "Docker commands", "phone": False},
    "aws": {"name": "☁️ AWS", "desc": "AWS cloud", "phone": False},
    "code": {"name": "💻 Code", "desc": "Write code", "phone": False},
    "debug": {"name": "🐛 Debug", "desc": "Debug code", "phone": False},
    "test": {"name": "🧪 Test", "desc": "Run tests", "phone": False},
    "git": {"name": "📦 Git", "desc": "Git operations", "phone": False},
    "database": {"name": "🗄️ Database", "desc": "Database queries", "phone": False},
    "api": {"name": "🔌 API", "desc": "API development", "phone": False},
    "csv": {"name": "📊 CSV", "desc": "Analyze CSV", "phone": False},
    "json": {"name": "📋 JSON", "desc": "Process JSON", "phone": False},
    "html": {"name": "🌐 HTML", "desc": "Generate HTML", "phone": False},
    "css": {"name": "🎨 CSS", "desc": "CSS styling", "phone": False},
    "javascript": {"name": "💛 JavaScript", "desc": "JavaScript code", "phone": False},
    "python": {"name": "🐍 Python", "desc": "Python code", "phone": False},
    "markdown": {"name": "📝 Markdown", "desc": "Write markdown", "phone": False},
    "chart": {"name": "📊 Chart", "desc": "Create charts", "phone": False},
    "report": {"name": "📄 Report", "desc": "Generate reports", "phone": False},
    "resume": {"name": "📄 Resume", "desc": "Create resume", "phone": False},
    "blog": {"name": "📝 Blog", "desc": "Write blog", "phone": False},
    "summary": {"name": "📋 Summary", "desc": "Summarize text", "phone": False},
    "grammar": {"name": "✅ Grammar", "desc": "Check grammar", "phone": False},
    "math": {"name": "📐 Math", "desc": "Solve math", "phone": False},
    "joke": {"name": "😂 Joke", "desc": "Tell a joke", "phone": False},
    "quote": {"name": "💬 Quote", "desc": "Get quote", "phone": False},
    "fact": {"name": "💡 Fact", "desc": "Random fact", "phone": False},
}

# Register all skills with orchestrator
for sid, skill in SKILLS.items():
    orchestrator.register_skill(sid, skill)

# WebSocket handler for phone
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    try:
        msg = await ws.receive()
        if msg.type == web.WSMsgType.TEXT:
            phone_id = msg.data
            orchestrator.arms.set_connection(ws)
            print(f"📱 Phone connected: {phone_id}")
            await ws.send_str(json.dumps({"type": "welcome", "heart": "beating"}))
            
            async for response in ws:
                if response.type == web.WSMsgType.TEXT:
                    print(f"📱 Response: {response.data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        orchestrator.arms.connected = False
    return ws

async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI - Full System</title>
        <style>
            body {{ background: linear-gradient(135deg, #0a0a0a, #1a1a2e); font-family: monospace; text-align: center; padding: 50px; color: #0f0; }}
            h1 {{ font-size: 3em; background: linear-gradient(135deg, #00ff9d, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .stats {{ display: flex; justify-content: center; gap: 20px; margin: 30px; }}
            .card {{ background: rgba(0,255,157,0.1); padding: 20px; border-radius: 16px; }}
            .heart {{ color: #ff3366; animation: pulse 1s infinite; }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
            input {{ padding: 12px; width: 400px; background: #2a2a2a; border: 1px solid #00ff9d; border-radius: 8px; color: white; }}
            button {{ padding: 12px 24px; background: #00ff9d; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }}
            .voice-btn {{ background: #ff9900; margin-left: 10px; }}
            .result {{ margin-top: 30px; padding: 20px; background: #1a1a1a; border-radius: 12px; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <div class="card">❤️ <span class="heart">HEART</span><br>Memory Active</div>
            <div class="card">🦾 ARMS<br>Phone: {'✅' if orchestrator.arms.connected else '❌'}</div>
            <div class="card">🎼 ORCHESTRATOR<br>{len(SKILLS)} Skills</div>
        </div>
        
        <div>
            <input type="text" id="command" placeholder="Type or speak..." autocomplete="off">
            <button onclick="send()">⚡ RUN</button>
            <button class="voice-btn" onclick="startVoice()">🎤 VOICE</button>
        </div>
        
        <div id="result" class="result"></div>
        
        <script>
            async function send() {{
                const cmd = document.getElementById('command').value;
                if(!cmd) return;
                document.getElementById('result').innerHTML = '🔄 Processing...';
                const res = await fetch('/api/command', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{command: cmd}})
                }});
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }}
            
            function startVoice() {{
                if (!('webkitSpeechRecognition' in window)) {{
                    alert('Use Chrome or Edge for voice');
                    return;
                }}
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'en-US';
                recognition.start();
                recognition.onresult = (event) => {{
                    document.getElementById('command').value = event.results[0][0].transcript;
                    send();
                }};
            }}
            
            document.getElementById('command').onkeypress = (e) => {{
                if(e.key === 'Enter') send();
            }};
        </script>
    </body>
    </html>
    """, content_type="text/html")

async def api_command(request):
    data = await request.json()
    command = data.get("command", "")
    
    # Orchestrator processes everything
    result = await orchestrator.process(command)
    
    return web.json_response(result)

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/api/command', api_command)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
print(f"\n{'='*50}")
print(f"🧠 NEXUS AI - FULL SYSTEM")
print(f"❤️ HEART: Memory Active")
print(f"🦾 ARMS: Phone Ready")
print(f"🎼 ORCHESTRATOR: {len(SKILLS)} Skills")
print(f"{'='*50}\n")
web.run_app(app, port=port)
