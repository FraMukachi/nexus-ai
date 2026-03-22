#!/usr/bin/env python3
import os
import json
from aiohttp import web

phones = []

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

async def index(request):
    return web.Response(text=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEXUS AI</title>
        <style>
            body {{ background: linear-gradient(135deg, #0a0a0a, #1a1a2e); font-family: monospace; text-align: center; padding: 50px; color: #0f0; }}
            h1 {{ font-size: 3em; background: linear-gradient(135deg, #00ff9d, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .stats {{ display: flex; justify-content: center; gap: 20px; margin: 30px; }}
            .card {{ background: rgba(0,255,157,0.1); padding: 20px; border-radius: 16px; }}
            input, button {{ padding: 12px; border-radius: 8px; }}
            input {{ width: 400px; background: #2a2a2a; border: 1px solid #00ff9d; color: white; }}
            button {{ background: #00ff9d; border: none; cursor: pointer; font-weight: bold; }}
            .voice-btn {{ background: #ff9900; margin-left: 10px; }}
            .result {{ margin-top: 30px; padding: 20px; background: #1a1a1a; border-radius: 12px; }}
        </style>
    </head>
    <body>
        <h1>🧠 NEXUS AI</h1>
        <div class="stats">
            <div class="card">❤️ HEART<br>Learning</div>
            <div class="card">🦾 ARMS<br>Phone: {'✅' if phones else '❌'}</div>
            <div class="card">🎼 ORCHESTRATOR<br>Skills Loading...</div>
        </div>
        
        <div>
            <input type="text" id="command" placeholder="Type or speak..." autocomplete="off">
            <button onclick="send()">⚡ RUN</button>
            <button class="voice-btn" onclick="startVoice()">🎤 VOICE</button>
        </div>
        
        <div id="result" class="result">Ready...</div>
        
        <script>
            async function send() {{
                const cmd = document.getElementById('command').value;
                if(!cmd) return;
                document.getElementById('result').innerHTML = '🔄 Processing...';
                const res = await fetch('/cmd', {{method: 'POST', body: cmd}});
                const data = await res.text();
                document.getElementById('result').innerHTML = data;
            }}
            
            function startVoice() {{
                if (!('webkitSpeechRecognition' in window)) {{
                    alert('Use Chrome or Edge for voice');
                    return;
                }}
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'en-US';
                recognition.start();
                recognition.onresult = (event) => {{
                    document.getElementById('command').value = event.results[0][0].transcript;
                    send();
                }};
            }}
            
            document.getElementById('command').onkeypress = (e) => {{
                if(e.key === 'Enter') send();
            }};
        </script>
    </body>
    </html>
    """, content_type="text/html")

async def cmd_handler(request):
    cmd = await request.text()
    cmd_lower = cmd.lower()
    
    if "flashlight" in cmd_lower:
        if phones:
            for ws in phones:
                try:
                    await ws.send_str(json.dumps({"action": "flashlight"}))
                except:
                    pass
            return web.Response(text="✅ Flashlight sent to phone!")
        return web.Response(text="❌ No phone connected")
    
    if "battery" in cmd_lower:
        return web.Response(text="🔋 Battery: 85% (demo)")
    
    if "joke" in cmd_lower:
        return web.Response(text="😂 Why did the AI cross the road? To control the chicken!")
    
    if "weather" in cmd_lower:
        return web.Response(text="🌤️ Sunny, 72°F")
    
    return web.Response(text=f"✅ Received: {cmd}")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
web.run_app(app, port=port)
