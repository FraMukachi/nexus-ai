# Memory System - The HEART of NEXUS AI
import sqlite3
import json
from datetime import datetime

class MemorySystem:
    def __init__(self):
        self.db = sqlite3.connect("nexus_brain.db")
        self._init_db()
    
    def _init_db(self):
        c = self.db.cursor()
        # Long-term memory
        c.execute('''CREATE TABLE IF NOT EXISTS long_term (
            id INTEGER PRIMARY KEY,
            fact TEXT,
            timestamp TEXT,
            importance REAL
        )''')
        # Conversation history
        c.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            command TEXT,
            skill_used TEXT,
            result TEXT,
            timestamp TEXT
        )''')
        # Learned patterns
        c.execute('''CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY,
            trigger TEXT,
            action TEXT,
            success_count INTEGER
        )''')
        self.db.commit()
    
    def remember(self, fact, importance=0.5):
        c = self.db.cursor()
        c.execute("INSERT INTO long_term (fact, timestamp, importance) VALUES (?, ?, ?)",
                  (fact, datetime.now().isoformat(), importance))
        self.db.commit()
    
    def recall(self, query):
        c = self.db.cursor()
        c.execute("SELECT fact FROM long_term ORDER BY importance DESC LIMIT 5")
        return [row[0] for row in c.fetchall()]
    
    def log_command(self, command, skill, result):
        c = self.db.cursor()
        c.execute("INSERT INTO history (command, skill_used, result, timestamp) VALUES (?, ?, ?, ?)",
                  (command, skill, result, datetime.now().isoformat()))
        self.db.commit()
    
    def learn_pattern(self, trigger, action):
        c = self.db.cursor()
        c.execute("INSERT INTO patterns (trigger, action, success_count) VALUES (?, ?, 1) "
                  "ON CONFLICT(trigger, action) DO UPDATE SET success_count = success_count + 1",
                  (trigger, action))
        self.db.commit()
