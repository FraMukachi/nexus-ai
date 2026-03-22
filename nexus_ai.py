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
        self.db = sqlite3.connect("nexus.db")
        c = self.db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER, cmd TEXT, skill TEXT, time TEXT)')
        self.db.commit()
        print(f"✅ Started | Skills: {self.total}")

ai = NexusAI()

# WebSocket handler
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    phone_id = None
    print("📱 New WebSocket connection")
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                if phone_id is None:
                    phone_id = msg.data
                    ai.phones[phone_id] = ws
                    print(f"✅ Phone connected: {phone_id}")
                    await ws.send(json.dumps({"status": "connected"}))
                else:
                    print(f"📱 From phone: {msg.data}")
                    # Keep connection alive
                    await ws.send(json.dumps({"status": "ok"}))
            elif msg.type == web.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        print(f"WebSocket exception: {e}")
    finally:
        if phone_id and phone_id in ai.phones:
            del ai.phones[phone_id]
            print(f"❌ Phone disconnected: {phone_id}")
    
    return ws

# Web pages
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
    
    # Find skill
    for sid, skill in SKILLS.items():
        if sid in cmd.lower():
            # If phone connected, execute
            if ai.phones and sid in ["flashlight", "battery", "vibrate"]:
                for phone_id, ws in list(ai.phones.items()):
                    try:
                        await ws.send(json.dumps({"command": sid}))
                        return web.Response(text=f"✅ Sent {skill['name']} to phone")
                    except:
                        pass
            return web.Response(text=f"✅ {skill['name']} - {skill['desc']}")
    
    return web.Response(text="❌ No skill found")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
