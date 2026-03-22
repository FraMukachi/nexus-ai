# Orchestrator - The BRAIN that coordinates all skills
import json
from memory import MemorySystem
from arms import PhoneArms

class Orchestrator:
    def __init__(self):
        self.memory = MemorySystem()  # Heart
        self.arms = PhoneArms()       # Limbs
        self.skills = {}              # All skills
        self.context = []             # Current conversation
        
    def register_skill(self, skill_id, skill_data):
        """Register a skill for use"""
        self.skills[skill_id] = skill_data
    
    async def process(self, command):
        """Main processing pipeline"""
        
        # 1. Recall past context
        past = self.memory.recall(command)
        
        # 2. Find matching skill
        skill = self._find_skill(command)
        
        # 3. Execute with arms if phone skill
        result = None
        if skill and skill.get("phone"):
            result = await self.arms.execute(skill["id"])
        elif skill:
            result = skill["desc"]
        
        # 4. Store in memory
        self.memory.log_command(command, skill["name"] if skill else "none", str(result))
        
        # 5. Learn pattern
        if skill:
            self.memory.learn_pattern(command, skill["id"])
        
        return {
            "skill": skill["name"] if skill else None,
            "result": result,
            "memory": past[:3]
        }
    
    def _find_skill(self, command):
        """Find best matching skill"""
        cmd_lower = command.lower()
        for sid, skill in self.skills.items():
            if sid in cmd_lower or skill["name"].lower() in cmd_lower:
                return {"id": sid, "name": skill["name"], "desc": skill["desc"], "phone": skill.get("phone", False)}
        return None

# Create global orchestrator
orchestrator = Orchestrator()
