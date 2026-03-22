#!/usr/bin/env python3
import os
import json
import asyncio
from aiohttp import web

phones = []

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("📱 Phone connecting...")
    phones.append(ws)
    print(f"📱 Total phones: {len(phones)}")
    
    try:
        # Send welcome
        await ws.send_str(json.dumps({"type": "welcome"}))
        
        # Keep connection alive - wait for messages forever
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                print(f"📱 Phone says: {msg.data}")
            elif msg.type == web.WSMsgType.CLOSE:
                break
            elif msg.type == web.WSMsgType.ERROR:
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ws in phones:
            phones.remove(ws)
        print(f"📱 Phone disconnected. Total: {len(phones)}")
    
    return ws

async def index(request):
    return web.Response(text=f"""
    <html><body style="background:#0a0a0a;color:#0f0;text-align:center;padding:50px">
    <h1>🧠 NEXUS AI</h1>
    <h2>Phones: {len(phones)}</h2>
    <input id="cmd" style="padding:10px;width:300px">
    <button onclick="send()">Send</button>
    <div id="result"></div>
    <script>
    async function send() {{
        let cmd = document.getElementById('cmd').value;
        let res = await fetch('/cmd', {{method:'POST', body:cmd}});
        let data = await res.text();
        document.getElementById('result').innerHTML = data;
    }}
    </script>
    </body></html>
    """, content_type="text/html")

async def cmd_handler(request):
    cmd = await request.text()
    cmd = cmd.lower()
    
    if "flashlight" in cmd:
        if phones:
            sent = 0
            for ws in phones:
                try:
                    await ws.send_str(json.dumps({"action": "flashlight"}))
                    sent += 1
                except:
                    pass
            return web.Response(text=f"✅ Sent to {sent} phone(s)")
        return web.Response(text="❌ No phone connected")
    
    return web.Response(text=f"Unknown: {cmd}")

app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/cmd', cmd_handler)
app.router.add_get('/ws', websocket_handler)

port = int(os.environ.get("PORT", 8080))
print(f"Server on port {port}")
web.run_app(app, port=port)
