#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime

try:
    from aiohttp import web
except:
    import subprocess
    subprocess.run(["pip", "install", "aiohttp"])
    from aiohttp import web

try:
    from groq import Groq
except:
    Groq = None

# Simple skills
SKILLS = {
    "flashlight": {"name": "Flashlight", "desc": "Control flashlight"},
    "battery": {"name": "Battery", "desc": "Check battery"},
    "weather": {"name": "Weather", "desc": "Get weather"},
    "news": {"name": "News", "desc": "Get news"},
}

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.total = len(SKILLS)
        self.count = 0
        self.db = sqlite3.connect("nexus.db")
        c = self.db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER, cmd TEXT, skill TEXT, time TEXT)')
        self.db.commit()
        print(f"✅ NEXUS AI Started | Skills: {self.total}")
    
    def process(self, cmd):
        self.count += 1
        for sid in self.skills:
            if sid in cmd.lower():
                skill = self.skills[sid]
                return {"success": True, "skill": skill["name"], "desc": skill["desc"]}
        return {"success": False, "error": "No skill found"}

ai = NexusAI()

async def index(request):
    return web.Response(text=f"""
    <html>
    <body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <p>Skills: {ai.total} | Commands: {ai.count}</p>
    <form action="/cmd" method="post">
        <input type="text" name="cmd" style="width:300px;padding:10px">
        <button type="submit">Run</button>
    </form>
    </body>
    </html>
    """, content_type="text/html")

async def cmd_handler(request):
    data = await request.post()
    cmd = data.get("cmd", "")
    result = ai.process(cmd)
    return web.Response(text=f"<pre>{json.dumps(result, indent=2)}</pre><a href='/'>Back</a>", content_type="text/html")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)

port = int(os.environ.get("PORT", 8080))
print(f"Starting on port {port}")
web.run_app(app, port=port)
