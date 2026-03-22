#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web
import asyncio

# Try Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

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

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.total = len(SKILLS)
        self.count = 0
        self.phones = {}
        
        api_key = os.environ.get("GROQ_API_KEY")
        self.groq = Groq(api_key=api_key) if api_key and GROQ_AVAILABLE else None
        print(f"✅ Started | Skills: {self.total} | Groq: {'ON' if self.groq else 'OFF'}")
    
    async def understand_command(self, cmd):
        if not self.groq:
            return None
        skill_list = ", ".join(list(self.skills.keys())[:30])
        prompt = f"""User said: "{cmd}"
Choose the best skill from: {skill_list}
Return ONLY the skill name."""
        try:
            response = self.groq.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()
        except:
            return None

ai = NexusAI()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    phone_id = None
    try:
        msg = await ws.receive()
        if msg.type == web.WSMsgType.TEXT:
            phone_id = msg.data
            ai.phones[phone_id] = ws
            print(f"📱 Phone connected: {phone_id}")
            await ws.send_str(json.dumps({"status": "ok"}))
            async for response in ws:
                if response.type == web.WSMsgType.TEXT:
                    print(f"📱 From phone: {response.data}")
    except:
        pass
    finally:
        if phone_id and phone_id in ai.phones:
            del ai.phones[phone_id]
    return ws

async def send_to_phone(cmd):
    if not ai.phones:
        return False
    for ws in list(ai.phones.values()):
        try:
            await ws.send_str(json.dumps({"command": cmd}))
            return True
        except:
            continue
    return False

async def index(request):
    groq_status = "✅ ON" if ai.groq else "❌ OFF"
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <style>
            body {{ background: linear-gradient(135deg, #0a0a0a, #1a1a2e); font-family: monospace; text-align: center; padding: 50px; color: #0f0; }}
            h1 {{ font-size: 3em; background: linear-gradient(135deg, #00ff9d, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .stats {{ background: rgba(0,255,157,0.1); padding: 20px; border-radius: 16px; display: inline-block; margin: 10px; }}
            input, button {{ padding: 12px; border-radius: 8px; }}
            input {{ width: 400px; background: #2a2a2a; border: 1px solid #00ff9d; color: white; }}
            button {{ background: #00ff9d; border: none; cursor: pointer; font-weight: bold; margin-left: 10px; }}
            .voice-btn {{ background: #ff9900; color: black; }}
            .result {{ margin-top: 20px; padding: 15px; background: #1a1a1a; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <p>📚 Skills: {ai.total} | 📱 Phones: {len(ai.phones)} | ⚡ Groq: {groq_status}</p>
        </div>
        <div>
            <input type="text" id="command" placeholder="Type or click microphone and speak..." autocomplete="off" style="width: 400px;">
            <button onclick="sendCommand()">⚡ RUN</button>
            <button id="voiceBtn" class="voice-btn" onclick="startVoice()">🎤 VOICE</button>
        </div>
        <div id="result" class="result"></div>
        <script>
            async function sendCommand() {{
                const cmd = document.getElementById('command').value;
                if(!cmd) return;
                document.getElementById('result').innerHTML = 'Processing...';
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
                    alert('Voice not supported in this browser. Try Chrome or Edge.');
                    return;
                }}
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'en-US';
                recognition.start();
                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('command').value = transcript;
                    sendCommand();
                }};
                recognition.onerror = (event) => {{
                    alert('Error: ' + event.error);
                }};
            }}
            
            document.getElementById('command').onkeypress = (e) => {{
                if(e.key === 'Enter') sendCommand();
            }};
        </script>
    </body>
    </html>
    """, content_type="text/html")

async def api_command(request):
    data = await request.json()
    cmd = data.get("command", "")
    
    understood = await ai.understand_command(cmd)
    skill_id = understood if understood in ai.skills else None
    
    if not skill_id:
        for sid in ai.skills:
            if sid in cmd.lower():
                skill_id = sid
                break
    
    if not skill_id:
        return web.json_response({"success": False, "error": "No skill found", "command": cmd})
    
    skill = ai.skills[skill_id]
    
    if skill.get("phone"):
        sent = await send_to_phone(skill_id)
        if sent:
            return web.json_response({"success": True, "skill": skill["name"], "action": f"Sent to phone: {skill['desc']}"})
        else:
            return web.json_response({"success": True, "skill": skill["name"], "action": skill["desc"], "warning": "No phone connected"})
    
    return web.json_response({"success": True, "skill": skill["name"], "action": skill["desc"]})

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/api/command', api_command)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
