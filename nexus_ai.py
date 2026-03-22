#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web

from full_skills import FULL_SKILLS
SKILLS = FULL_SKILLS

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.total = len(SKILLS)
        self.count = 0
        self.phones = {}
        print(f"✅ Started | Skills: {self.total}")

ai = NexusAI()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    phone_id = None
    print("📱 New connection attempt")
    
    try:
        # Wait for first message (phone ID)
        msg = await ws.receive()
        if msg.type == web.WSMsgType.TEXT:
            phone_id = msg.data
            ai.phones[phone_id] = ws
            print(f"✅ Phone connected: {phone_id}")
            await ws.send_str(json.dumps({"status": "ok"}))
            
            # Keep connection alive and listen for responses
            async for response in ws:
                if response.type == web.WSMsgType.TEXT:
                    print(f"📱 From phone: {response.data}")
                elif response.type == web.WSMsgType.ERROR:
                    print(f"WebSocket error")
                    break
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if phone_id and phone_id in ai.phones:
            del ai.phones[phone_id]
            print(f"❌ Phone disconnected: {phone_id}")
    
    return ws

async def send_to_phone(cmd):
    """Send command to all connected phones"""
    if not ai.phones:
        return False
    for phone_id, ws in list(ai.phones.items()):
        try:
            await ws.send_str(json.dumps({"command": cmd}))
            return True
        except:
            continue
    return False

async def index(request):
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <p>Skills: {ai.total} | Phones: {len(ai.phones)}</p>
    <form action="/cmd" method="post">
        <input name="cmd" style="width:300px;padding:10px">
        <button type="submit">Run</button>
    </form>
    </body></html>
    """, content_type="text/html")

async def cmd_handler(request):
    data = await request.post()
    cmd = data.get("cmd", "")
    
    for sid, skill in SKILLS.items():
        if sid in cmd.lower():
            # Send to phone if available
            if sid in ["flashlight", "battery", "vibrate"]:
                sent = await send_to_phone(sid)
                if sent:
                    return web.Response(text=f"✅ Sent {skill['name']} to phone")
                else:
                    return web.Response(text=f"⚠️ {skill['name']} - No phone connected")
            return web.Response(text=f"✅ {skill['name']} - {skill['desc']}")
    
    return web.Response(text="❌ No skill found")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
print(f"🚀 Server on port {port}")
web.run_app(app, port=port)
