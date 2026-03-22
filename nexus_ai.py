#!/usr/bin/env python3
import os
import json
import asyncio
from aiohttp import web

SKILLS = {
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on flashlight", "phone": True},
    "battery": {"name": "🔋 Battery", "desc": "Check battery", "phone": True},
}

ai = {"phones": [], "skills": SKILLS}

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("📱 New WebSocket connection")
    ai["phones"].append(ws)
    
    try:
        # Send welcome
        await ws.send_str(json.dumps({"type": "welcome"}))
        
        # Keep alive - just wait for messages
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                print(f"📱 Phone says: {msg.data}")
            elif msg.type == web.WSMsgType.ERROR:
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ws in ai["phones"]:
            ai["phones"].remove(ws)
        print("📱 Phone disconnected")
    
    return ws

async def index(request):
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <p>Phones: {len(ai['phones'])}</p>
    <input id="cmd" placeholder="flashlight" style="padding:10px">
    <button onclick="send()">Run</button>
    <div id="result"></div>
    <script>
    async function send() {{
        let cmd = document.getElementById('cmd').value;
        let res = await fetch('/cmd', {{
            method: 'POST',
            body: cmd
        }});
        let data = await res.text();
        document.getElementById('result').innerHTML = data;
    }}
    </script>
    </body></html>
    """, content_type="text/html")

async def cmd_handler(request):
    cmd = await request.text()
    cmd = cmd.lower().strip()
    
    # Find skill
    for sid, skill in SKILLS.items():
        if sid in cmd:
            if skill.get("phone") and ai["phones"]:
                # Send to all connected phones
                for ws in ai["phones"]:
                    try:
                        await ws.send_str(json.dumps({"command": sid}))
                    except:
                        pass
                return web.Response(text=f"✅ Sent {skill['name']} to {len(ai['phones'])} phone(s)")
            return web.Response(text=f"✅ {skill['name']}: {skill['desc']}")
    
    return web.Response(text="❌ No skill found")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
