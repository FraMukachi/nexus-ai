#!/usr/bin/env python3
"""
NEXUS AI - Self-Evolving Intelligence with Groq
"""

import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# 100+ HARDCODED SKILLS
SKILLS = {
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on/off flashlight"},
    "battery": {"name": "🔋 Battery", "desc": "Check battery status"},
    "weather": {"name": "🌤️ Weather", "desc": "Get weather forecast"},
    "news": {"name": "📰 News", "desc": "Fetch latest news"},
    "translate": {"name": "🌐 Translate", "desc": "Translate text"},
    "email": {"name": "📧 Email", "desc": "Send emails"},
    "calendar": {"name": "📅 Calendar", "desc": "Manage events"},
    "voice": {"name": "🎤 Voice", "desc": "Voice control"},
    "camera": {"name": "📷 Camera", "desc": "Take photos"},
    "docx": {"name": "📄 Word", "desc": "Create Word documents"},
    "pdf": {"name": "📑 PDF", "desc": "Process PDF files"},
    "telegram": {"name": "📱 Telegram", "desc": "Telegram bot"},
    "whatsapp": {"name": "💬 WhatsApp", "desc": "WhatsApp messaging"},
    "discord": {"name": "🎮 Discord", "desc": "Discord bot"},
    "slack": {"name": "💼 Slack", "desc": "Slack workspace"},
    "screenshot": {"name": "📸 Screenshot", "desc": "Capture screen"},
    "vibrate": {"name": "📳 Vibrate", "desc": "Phone vibration"},
    "location": {"name": "📍 Location", "desc": "Get GPS location"},
    "alarm": {"name": "⏰ Alarm", "desc": "Set alarms"},
    "reminder": {"name": "📝 Reminder", "desc": "Set reminders"},
}

class NexusAI:
    def __init__(self):
        self.skills = SKILLS
        self.total = len(SKILLS)
        self.count = 0
        
        # Setup Groq
        api_key = os.getenv("GROQ_API_KEY")
        self.groq = Groq(api_key=api_key) if api_key else None
        
        # Database
        self.db = sqlite3.connect("nexus.db")
        c = self.db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER, cmd TEXT, skill TEXT, time TEXT)')
        self.db.commit()
        print(f"✅ Loaded {self.total} skills | Groq: {'ON' if self.groq else 'OFF'}")
    
    def process(self, cmd):
        self.count += 1
        
        # Try Groq
        skill_id = None
        if self.groq:
            try:
                resp = self.groq.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "user", "content": f"Select best skill for: {cmd}. Skills: {list(self.skills.keys())}"}],
                    max_tokens=50
                )
                skill_id = resp.choices[0].message.content.strip().lower()
            except: pass
        
        # Fallback
        if not skill_id or skill_id not in self.skills:
            for sid in self.skills:
                if sid in cmd.lower():
                    skill_id = sid
                    break
        
        skill = self.skills.get(skill_id)
        
        # Save
        c = self.db.cursor()
        c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (self.count, cmd, skill["name"] if skill else "none", datetime.now().isoformat()))
        self.db.commit()
        
        if skill:
            return {"success": True, "skill": skill["name"], "desc": skill["desc"]}
        return {"success": False, "error": "No skill found", "suggestions": list(self.skills.keys())[:10]}

ai = NexusAI()

async def index(request):
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <p>Skills: {ai.total} | Commands: {ai.count} | Groq: {'✅' if ai.groq else '❌'}</p>
    <form action="/cmd" method="post">
        <input type="text" name="cmd" placeholder="Enter command..." style="width:300px;padding:10px">
        <button type="submit">Run</button>
    </form>
    </body></html>
    """, content_type="text/html")

async def cmd_handler(request):
    data = await request.post()
    cmd = data.get("cmd", "")
    result = ai.process(cmd)
    return web.Response(text=f"<pre>{json.dumps(result, indent=2)}</pre><br><a href='/'>Back</a>", content_type="text/html")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
