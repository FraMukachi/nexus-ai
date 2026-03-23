#!/usr/bin/env python3
"""
NEXUS AI - Phone Client for Android Termux
Connects your phone to NEXUS AI for hardware control
"""

import asyncio
import websockets
import json
import subprocess

# Your Railway URL (change this to your deployed URL)
RAILWAY_URL = "nexus-ai-production-69ce.up.railway.app"

async def execute_command(cmd):
    """Execute phone hardware commands"""
    print(f"🔧 Executing: {cmd}")
    
    if cmd == "flashlight":
        subprocess.run(["termux-torch", "on"])
        return {"status": "flashlight on"}
    elif cmd == "flashlight_off":
        subprocess.run(["termux-torch", "off"])
        return {"status": "flashlight off"}
    elif cmd == "battery":
        result = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
        data = json.loads(result.stdout)
        return {"status": f"Battery: {data.get('percentage')}%"}
    elif cmd == "vibrate":
        subprocess.run(["termux-vibrate", "-d", "500"])
        return {"status": "vibrated"}
    elif cmd == "camera":
        subprocess.run(["termux-camera-photo", "/sdcard/nexus_photo.jpg"])
        return {"status": "photo taken"}
    elif cmd == "screenshot":
        subprocess.run(["termux-screenshot", "/sdcard/nexus_screenshot.png"])
        return {"status": "screenshot taken"}
    elif cmd == "volume_up":
        subprocess.run(["termux-volume", "music", "10"])
        return {"status": "volume up"}
    elif cmd == "volume_down":
        subprocess.run(["termux-volume", "music", "1"])
        return {"status": "volume down"}
    elif cmd == "wifi_on":
        subprocess.run(["termux-wifi-enable", "true"])
        return {"status": "wifi on"}
    elif cmd == "wifi_off":
        subprocess.run(["termux-wifi-enable", "false"])
        return {"status": "wifi off"}
    elif cmd == "bluetooth_on":
        subprocess.run(["termux-bluetooth-enable", "true"])
        return {"status": "bluetooth on"}
    elif cmd == "bluetooth_off":
        subprocess.run(["termux-bluetooth-enable", "false"])
        return {"status": "bluetooth off"}
    
    return {"status": "unknown"}

async def connect():
    url = f"wss://{RAILWAY_URL}/ws"
    print(f"🔌 Connecting to {url}...")
    
    while True:
        try:
            async with websockets.connect(url) as ws:
                await ws.send("my_android")
                print("✅ Connected! Waiting for commands...")
                
                async for msg in ws:
                    data = json.loads(msg)
                    print(f"📨 {data}")
                    
                    if "action" in data:
                        cmd = data["action"]
                        result = await execute_command(cmd)
                        await ws.send(json.dumps(result))
                        print(f"✅ Sent: {result}")
                        
        except Exception as e:
            print(f"❌ Error: {e}, reconnecting...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(connect())
