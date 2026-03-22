#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web
from full_skills import FULL_SKILLS

# Use full skills database
SKILLS = FULL_SKILLS

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
        cmd_lower = cmd.lower()
        
        # Find matching skill
        for sid, skill in self.skills.items():
            if sid in cmd_lower or skill["name"].lower() in cmd_lower:
                # Save to history
                c = self.db.cursor()
                c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", 
                         (self.count, cmd, skill["name"], datetime.now().isoformat()))
                self.db.commit()
                return {"success": True, "skill": skill["name"], "desc": skill["desc"]}
        
        # No match found
        return {"success": False, "error": "No skill found", "suggestions": list(self.skills.keys())[:10]}

ai = NexusAI()

async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                font-family: monospace;
                text-align: center;
                padding: 50px;
                color: #0f0;
            }}
            h1 {{
                font-size: 3em;
                background: linear-gradient(135deg, #00ff9d, #00d4ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .stats {{
                display: inline-block;
                background: rgba(0,255,157,0.1);
                padding: 20px;
                border-radius: 16px;
                margin: 20px 0;
            }}
            input {{
                padding: 12px;
                width: 300px;
                background: #2a2a2a;
                border: 1px solid #00ff9d;
                border-radius: 8px;
                color: white;
                font-family: monospace;
            }}
            button {{
                padding: 12px 24px;
                background: #00ff9d;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
            }}
            .skill-badge {{
                display: inline-block;
                background: rgba(0,255,157,0.2);
                padding: 5px 12px;
                border-radius: 20px;
                margin: 5px;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <p>📚 Skills: {ai.total} | 🎯 Commands: {ai.count}</p>
        </div>
        <form action="/cmd" method="post">
            <input type="text" name="cmd" placeholder="Enter command..." autocomplete="off">
            <button type="submit">⚡ RUN</button>
        </form>
        <div style="margin-top: 30px;">
            <p>Try: flashlight, battery, weather, news, translate, email, joke, quote, calculator</p>
        </div>
    </body>
    </html>
    """, content_type="text/html")

async def cmd_handler(request):
    data = await request.post()
    cmd = data.get("cmd", "")
    result = ai.process(cmd)
    return web.Response(text=f"""
    <html>
    <body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:50px">
        <h2>📝 Result</h2>
        <pre style="background:#1a1a1a;padding:20px;border-radius:8px">{json.dumps(result, indent=2)}</pre>
        <br>
        <a href="/" style="color:#00ff9d">← Back</a>
    </body>
    </html>
    """, content_type="text/html")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)

port = int(os.environ.get("PORT", 8080))
print(f"Starting NEXUS AI on port {port}")
web.run_app(app, port=port)
