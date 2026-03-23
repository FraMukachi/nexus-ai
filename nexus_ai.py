#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web
from security import security

# Skills
SKILLS = {
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on flashlight", "phone": True},
    "battery": {"name": "🔋 Battery", "desc": "Check battery", "phone": True},
    "vibrate": {"name": "📳 Vibrate", "desc": "Make phone vibrate", "phone": True},
    "weather": {"name": "🌤️ Weather", "desc": "Get weather", "phone": False},
    "joke": {"name": "😂 Joke", "desc": "Tell a joke", "phone": False},
    "quote": {"name": "💬 Quote", "desc": "Get quote", "phone": False},
}

# Simple phone storage
phones = []

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    phones.append(ws)
    print(f"📱 Phone connected. Total: {len(phones)}")
    
    try:
        await ws.send_str(json.dumps({"type": "welcome"}))
        
        # Keep connection alive - just wait
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                print(f"📱 Phone: {msg.data}")
            elif msg.type == web.WSMsgType.CLOSE:
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ws in phones:
            phones.remove(ws)
        print(f"📱 Phone disconnected. Total: {len(phones)}")
    
    return ws

async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <style>
            body {{ background: #0a0a0a; font-family: monospace; text-align: center; padding: 50px; color: #0f0; }}
            h1 {{ color: #00ff9d; }}
            .card {{ background: #1a1a1a; padding: 20px; border-radius: 16px; display: inline-block; margin: 10px; }}
            input {{ padding: 12px; width: 300px; background: #2a2a2a; border: 1px solid #00ff9d; color: white; }}
            button {{ padding: 12px 24px; background: #00ff9d; border: none; cursor: pointer; }}
            .voice-btn {{ background: #ff9900; margin-left: 10px; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="card">🦾 ARMS<br>Phone: {'✅' if phones else '❌'}</div>
        <div class="card">🎼 ORCHESTRATOR<br>{len(SKILLS)} Skills</div>
        <br><br>
        <input type="text" id="cmd" placeholder="Type or speak...">
        <button onclick="send()">RUN</button>
        <button class="voice-btn" onclick="startVoice()">🎤 VOICE</button>
        <div id="result" style="margin-top: 20px;"></div>
        <script>
            async function send() {{
                let cmd = document.getElementById('cmd').value;
                let res = await fetch('/api', {{method: 'POST', body: cmd}});
                let data = await res.text();
                document.getElementById('result').innerHTML = data;
            }}
            function startVoice() {{
                let r = new webkitSpeechRecognition();
                r.lang = 'en-US';
                r.start();
                r.onresult = (e) => {{
                    document.getElementById('cmd').value = e.results[0][0].transcript;
                    send();
                }};
            }}
        </script>
    </body>
    </html>
    """, content_type="text/html")

async def api_handler(request):
    cmd = await request.text()
    cmd_lower = cmd.lower()
    
    # Find skill
    for sid, skill in SKILLS.items():
        if sid in cmd_lower:
            if skill.get("phone") and phones:
                for ws in phones:
                    try:
                        await ws.send_str(json.dumps({"action": sid}))
                    except:
                        pass
                return web.Response(text=f"✅ {skill['name']} sent to {len(phones)} phone(s)")
            return web.Response(text=f"✅ {skill['name']}: {skill['desc']}")
    
    return web.Response(text=f"❌ No skill for: {cmd}")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/api', api_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
