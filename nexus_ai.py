#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web, web_ws
from full_skills import FULL_SKILLS

SKILLS = FULL_SKILLS

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.total = len(SKILLS)
        self.count = 0
        self.phones = {}  # Store connected phones
        self.db = sqlite3.connect("nexus.db")
        c = self.db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER, cmd TEXT, skill TEXT, time TEXT)')
        self.db.commit()
        print(f"✅ NEXUS AI Started | Skills: {self.total}")
    
    def process(self, cmd):
        self.count += 1
        cmd_lower = cmd.lower()
        for sid, skill in self.skills.items():
            if sid in cmd_lower or skill["name"].lower() in cmd_lower:
                c = self.db.cursor()
                c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", 
                         (self.count, cmd, skill["name"], datetime.now().isoformat()))
                self.db.commit()
                return {"success": True, "skill": skill["name"], "desc": skill["desc"], "skill_id": sid}
        return {"success": False, "error": "No skill found", "suggestions": list(self.skills.keys())[:10]}

ai = NexusAI()

# WebSocket handler for phone connections
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    phone_id = None
    async for msg in ws:
        if msg.type == web_ws.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if phone_id is None:
                phone_id = data
                ai.phones[phone_id] = ws
                print(f"📱 Phone connected: {phone_id}")
            else:
                print(f"📱 Response from {phone_id}: {data}")
    
    if phone_id:
        del ai.phones[phone_id]
        print(f"📱 Phone disconnected: {phone_id}")
    
    return ws

# Web handler
async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <style>
            body {{
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                font-family: monospace;
                text-align: center;
                padding: 50px;
                color: #0f0;
            }}
            h1 {{ font-size: 3em; background: linear-gradient(135deg, #00ff9d, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .stats {{ background: rgba(0,255,157,0.1); padding: 20px; border-radius: 16px; display: inline-block; }}
            input {{ padding: 12px; width: 300px; background: #2a2a2a; border: 1px solid #00ff9d; border-radius: 8px; color: white; }}
            button {{ padding: 12px 24px; background: #00ff9d; border: none; border-radius: 8px; cursor: pointer; }}
            .phone-status {{ margin-top: 20px; padding: 10px; background: #1a1a1a; border-radius: 8px; display: inline-block; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <p>📚 Skills: {ai.total} | 🎯 Commands: {ai.count} | 📱 Phones: {len(ai.phones)}</p>
        </div>
        <div class="phone-status">
            🟢 Phone: {'Connected' if len(ai.phones) > 0 else 'Disconnected'}
        </div>
        <form action="/cmd" method="post">
            <input type="text" name="cmd" placeholder="Enter command..." autocomplete="off">
            <button type="submit">⚡ RUN</button>
        </form>
    </body>
    </html>
    """, content_type="text/html")

async def cmd_handler(request):
    data = await request.post()
    cmd = data.get("cmd", "")
    result = ai.process(cmd)
    
    # If phone connected and command is actionable
    if result.get("success") and ai.phones:
        skill_id = result.get("skill_id")
        if skill_id in ["flashlight", "battery", "vibrate"]:
            for phone_id, ws in ai.phones.items():
                try:
                    await ws.send(json.dumps({"command": skill_id}))
                    result["executed_on_phone"] = True
                except:
                    result["executed_on_phone"] = False
    
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:50px">
        <pre>{json.dumps(result, indent=2)}</pre>
        <br><a href="/" style="color:#00ff9d">← Back</a>
    </body></html>
    """, content_type="text/html")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
print(f"🚀 NEXUS AI on port {port}")
print(f"📱 WebSocket: ws://localhost:{port}/ws")
web.run_app(app, port=port)
