#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from aiohttp import web

# ========== ALL SKILLS (Add new ones here) ==========
SKILLS = {
    # Hardware Skills
    "flashlight": {"name": "🔦 Flashlight", "desc": "Turn on flashlight", "phone": True},
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
    
    # Entertainment Skills
    "joke": {"name": "😂 Joke", "desc": "Tell a funny joke", "phone": False},
    "quote": {"name": "💬 Quote", "desc": "Inspirational quote", "phone": False},
    "fact": {"name": "💡 Fact", "desc": "Random interesting fact", "phone": False},
    "trivia": {"name": "❓ Trivia", "desc": "Fun trivia question", "phone": False},
    "riddle": {"name": "🤔 Riddle", "desc": "Ask a riddle", "phone": False},
    
    # General Skills
    "weather": {"name": "🌤️ Weather", "desc": "Weather forecast", "phone": False},
    "news": {"name": "📰 News", "desc": "Latest headlines", "phone": False},
    "translate": {"name": "🌐 Translate", "desc": "Translate text", "phone": False},
    "calculate": {"name": "🧮 Calculate", "desc": "Do math calculations", "phone": False},
    "time": {"name": "🕐 Time", "desc": "Current time", "phone": False},
    "date": {"name": "📅 Date", "desc": "Today's date", "phone": False},
    "search": {"name": "🔍 Search", "desc": "Search the internet", "phone": False},
    "email": {"name": "📧 Email", "desc": "Send an email", "phone": False},
    "calendar": {"name": "📅 Calendar", "desc": "Manage calendar events", "phone": False},
    "note": {"name": "📝 Note", "desc": "Save a note", "phone": False},
    "reminder": {"name": "⏰ Reminder", "desc": "Set a reminder", "phone": False},
    "alarm": {"name": "⏰ Alarm", "desc": "Set an alarm", "phone": False},
    "timer": {"name": "⏱️ Timer", "desc": "Set a timer", "phone": False},
    "stopwatch": {"name": "⏱️ Stopwatch", "desc": "Start stopwatch", "phone": False},
    
    # Information Skills
    "definition": {"name": "📖 Definition", "desc": "Get word definition", "phone": False},
    "synonym": {"name": "🔄 Synonym", "desc": "Find synonyms", "phone": False},
    "antonym": {"name": "🔀 Antonym", "desc": "Find antonyms", "phone": False},
    "spell": {"name": "🔤 Spell", "desc": "Spell a word", "phone": False},
    "grammar": {"name": "✅ Grammar", "desc": "Check grammar", "phone": False},
    
    # Code Skills
    "code": {"name": "💻 Code", "desc": "Write code", "phone": False},
    "debug": {"name": "🐛 Debug", "desc": "Debug code", "phone": False},
    "explain": {"name": "📚 Explain", "desc": "Explain code", "phone": False},
    
    # Utility Skills
    "qrcode": {"name": "📷 QR Code", "desc": "Generate QR code", "phone": False},
    "password": {"name": "🔐 Password", "desc": "Generate password", "phone": False},
    "random": {"name": "🎲 Random", "desc": "Random number", "phone": False},
    "flip": {"name": "🪙 Flip coin", "desc": "Flip a coin", "phone": False},
    "roll": {"name": "🎲 Roll dice", "desc": "Roll dice", "phone": False},
}

# ========== Simple Phone Storage ==========
phones = []

# ========== WEBSOCKET ==========
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    phones.append(ws)
    print(f"📱 Phone connected. Total: {len(phones)}")
    try:
        await ws.send_str(json.dumps({"type": "welcome"}))
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                print(f"📱 Phone: {msg.data}")
    except:
        pass
    finally:
        if ws in phones:
            phones.remove(ws)
        print(f"📱 Phone disconnected. Total: {len(phones)}")
    return ws

# ========== WEB UI ==========
async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <style>
            body {{ background: #0a0a0a; font-family: monospace; text-align: center; padding: 50px; color: #0f0; }}
            h1 {{ color: #00ff9d; }}
            .stats {{ display: flex; justify-content: center; gap: 20px; margin: 20px; flex-wrap: wrap; }}
            .card {{ background: #1a1a1a; padding: 15px; border-radius: 12px; }}
            input {{ padding: 12px; width: 400px; background: #2a2a2a; border: 1px solid #00ff9d; color: white; border-radius: 8px; }}
            button {{ padding: 12px 24px; background: #00ff9d; border: none; cursor: pointer; border-radius: 8px; font-weight: bold; }}
            .voice-btn {{ background: #ff9900; margin-left: 10px; }}
            .result {{ margin-top: 20px; padding: 20px; background: #1a1a1a; border-radius: 12px; }}
            .skill-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 20px; }}
            .skill-badge {{ background: #2a2a2a; padding: 8px; border-radius: 8px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <div class="card">🦾 ARMS<br>Phone: {'✅' if phones else '❌'}</div>
            <div class="card">🎼 SKILLS<br>{len(SKILLS)} Available</div>
            <div class="card">🤖 AGENTS<br>Hardware | Entertainment | General</div>
        </div>
        <div>
            <input type="text" id="cmd" placeholder="Try: joke, weather, battery, flashlight, quote, fact, time..." autocomplete="off">
            <button onclick="send()">⚡ RUN</button>
            <button class="voice-btn" onclick="startVoice()">🎤 VOICE</button>
        </div>
        <div id="result" class="result">Ready...</div>
        <div class="skill-grid">
            <div class="skill-badge">🔦 flashlight</div>
            <div class="skill-badge">😂 joke</div>
            <div class="skill-badge">🌤️ weather</div>
            <div class="skill-badge">🔋 battery</div>
            <div class="skill-badge">💬 quote</div>
            <div class="skill-badge">💡 fact</div>
            <div class="skill-badge">🕐 time</div>
            <div class="skill-badge">📅 date</div>
            <div class="skill-badge">📳 vibrate</div>
            <div class="skill-badge">🌐 translate</div>
            <div class="skill-badge">📰 news</div>
            <div class="skill-badge">🧮 calculate</div>
            <div class="skill-badge">🔍 search</div>
            <div class="skill-badge">📧 email</div>
            <div class="skill-badge">📝 note</div>
            <div class="skill-badge">⏰ reminder</div>
        </div>
        <script>
            async function send() {{
                let cmd = document.getElementById('cmd').value;
                if(!cmd) return;
                document.getElementById('result').innerHTML = '🔄 Processing...';
                let res = await fetch('/api', {{method: 'POST', body: cmd}});
                let data = await res.text();
                document.getElementById('result').innerHTML = '<pre>' + data + '</pre>';
            }}
            function startVoice() {{
                if (!('webkitSpeechRecognition' in window)) {{ alert('Use Chrome'); return; }}
                let r = new webkitSpeechRecognition();
                r.lang = 'en-US';
                r.start();
                r.onresult = (e) => {{
                    document.getElementById('cmd').value = e.results[0][0].transcript;
                    send();
                }};
            }}
            document.getElementById('cmd').onkeypress = (e) => {{ if(e.key === 'Enter') send(); }};
        </script>
    </body>
    </html>
    """, content_type="text/html")

# ========== API HANDLER ==========
async def api_handler(request):
    cmd = await request.text()
    cmd_lower = cmd.lower()
    
    # Find matching skill
    for sid, skill in SKILLS.items():
        if sid in cmd_lower or skill["name"].lower() in cmd_lower:
            # Execute
            if skill.get("phone") and phones:
                for ws in phones:
                    try:
                        await ws.send_str(json.dumps({"action": sid}))
                    except:
                        pass
                return web.Response(text=f"✅ {skill['name']} sent to {len(phones)} phone(s)\n\n{skill['desc']}")
            else:
                # Demo responses for non-phone skills
                if sid == "joke":
                    response = "Why did the AI cross the road? To control the chicken!"
                elif sid == "quote":
                    response = "The only way to do great work is to love what you do. - Steve Jobs"
                elif sid == "fact":
                    response = "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs!"
                elif sid == "time":
                    from datetime import datetime
                    response = f"Current time: {datetime.now().strftime('%I:%M %p')}"
                elif sid == "date":
                    from datetime import datetime
                    response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
                elif sid == "weather":
                    response = "🌤️ Sunny, 72°F. Perfect weather!"
                elif sid == "news":
                    response = "📰 Latest: AI agents are revolutionizing personal assistants!"
                elif sid == "calculate":
                    response = "🧮 Math calculation ready"
                elif sid == "translate":
                    response = "🌐 Translation ready"
                else:
                    response = skill["desc"]
                return web.Response(text=f"✅ {skill['name']}\n\n{response}")
    
    return web.Response(text=f"❌ No skill found for: '{cmd}'\n\nTry: flashlight, joke, weather, battery, quote, fact, time, date")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/api', api_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
print(f"\n{'='*50}")
print(f"🧠 NEXUS AI - {len(SKILLS)} SKILLS READY")
print(f"📱 Phone: {'Connected' if phones else 'Waiting'}")
print(f"🎤 Voice: Click microphone button")
print(f"{'='*50}\n")
web.run_app(app, port=port)
