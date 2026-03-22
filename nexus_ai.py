#!/usr/bin/env python3
import os
import json
from aiohttp import web

SKILLS = {
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on flashlight", "phone": True},
    "battery": {"name": "🔋 Battery", "desc": "Check battery", "phone": True},
    "weather": {"name": "🌤️ Weather", "desc": "Weather forecast", "phone": False},
    "news": {"name": "📰 News", "desc": "Latest news", "phone": False},
    "joke": {"name": "😂 Joke", "desc": "Tell a joke", "phone": False},
}

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.phones = {}
        print(f"✅ Started | Skills: {len(SKILLS)}")

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
            await ws.send_str(json.dumps({"type": "welcome"}))
            
            # Keep connection alive - just wait
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    print(f"📱 From phone: {msg.data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if phone_id and phone_id in ai.phones:
            del ai.phones[phone_id]
            print(f"📱 Phone disconnected: {phone_id}")
    return ws

async def index(request):
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <p>Phones: {len(ai.phones)}</p>
    <input id="cmd" placeholder="Command..." style="padding:10px;width:300px">
    <button onclick="send()">Run</button>
    <div id="result"></div>
    <script>
    async function send() {{
        let cmd = document.getElementById('cmd').value;
        let res = await fetch('/api/command', {{
            method: 'POST',
            body: JSON.stringify({{command: cmd}}),
            headers: {{'Content-Type': 'application/json'}}
        }});
        let data = await res.json();
        document.getElementById('result').innerHTML = JSON.stringify(data);
    }}
    </script>
    </body></html>
    """, content_type="text/html")

async def api_command(request):
    data = await request.json()
    cmd = data.get("command", "").lower()
    
    for sid, skill in SKILLS.items():
        if sid in cmd:
            if skill.get("phone") and ai.phones:
                # Send to phone
                for ws in ai.phones.values():
                    await ws.send_str(json.dumps({"command": sid}))
                return web.json_response({"success": True, "skill": skill["name"], "sent_to_phone": True})
            return web.json_response({"success": True, "skill": skill["name"], "desc": skill["desc"]})
    
    return web.json_response({"success": False, "error": "No skill found"})

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/api/command', api_command)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
