# Arms System - Executes commands on phone
import subprocess
import json

class PhoneArms:
    def __init__(self):
        self.connected = False
        self.websocket = None
    
    def set_connection(self, ws):
        self.websocket = ws
        self.connected = True
    
    async def execute(self, command):
        if not self.connected:
            return {"error": "No phone connected"}
        
        try:
            await self.websocket.send(json.dumps({"command": command}))
            return {"status": "sent", "command": command}
        except Exception as e:
            return {"error": str(e)}
    
    def execute_local(self, command):
        """Execute commands locally (for testing)"""
        if command == "flashlight":
            # This would be termux command
            return {"status": "flashlight toggled"}
        return {"status": "unknown"}
