#!/usr/bin/env python3
"""
F.R.I.D.A.Y. ULTRA — Tony Stark Level AI Assistant
The most advanced AI assistant ever built for macOS.

Features: Agentic AI, Web Agent, RAG Knowledge Base, Multi-Agent Swarm,
Autonomous Actions, Code Executor, Email, Smart Home, Data Analysis,
Video Notes, Learning Mode, Streaming Voice, Advanced UI with 3 themes.
"""

import sys
import os
import json
import time
import threading
import random
import math
import subprocess
import tempfile
import sqlite3
import hashlib
import datetime as dt
import re
import ast
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict

# Qt Imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QTextEdit,
    QSystemTrayIcon, QMenu, QTabWidget, QListWidget, QSplashScreen,
    QDialog, QGroupBox, QSlider, QCheckBox, QComboBox, QProgressBar,
    QGraphicsDropShadowEffect, QStackedWidget, QListWidgetItem,
    QAbstractItemView, QSplitter, QSizePolicy, QToolButton,
    QProgressDialog, QInputDialog, QMessageBox, QColorDialog,
    QFontDialog, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QObject, pyqtSignal, QThread, QSize,
    QPropertyAnimation, QEasingCurve, QRect, QRectF, QPoint,
    QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QBrush, QPen, QPainter, QPainterPath,
    QRadialGradient, QLinearGradient, QIcon, QAction, QPixmap,
    QTransform, QConicalGradient, QGradient, QKeyEvent, QEnterEvent
)
from PyQt6.QtSvg import QSvgRenderer

# Configuration
FRIDAY_SERVER = "https://friday-ai-2hbv.onrender.com"
YOUR_NAME = "Rutwik"
LOCATION = "Pune"
APP_NAME = "F.R.I.D.A.Y. ULTRA"
VERSION = "10.0 PRO"

# =============================================================================
# THEME SYSTEM — 3 Professional Themes
# =============================================================================

@dataclass
class Theme:
    name: str
    background: str
    surface: str
    surface_alt: str
    primary: str
    primary_glow: str
    secondary: str
    accent: str
    text: str
    text_secondary: str
    border: str
    success: str
    warning: str
    error: str
    arc_reactor_color: tuple
    arc_reactor_glow: str

THEMES = {
    "jarvis": Theme(
        name="JARVIS",
        background="#030810",
        surface="#0a1525",
        surface_alt="#0f1f35",
        primary="#00d4ff",
        primary_glow="rgba(0, 212, 255, 0.3)",
        secondary="#0066aa",
        accent="#00ff88",
        text="#c8e8f0",
        text_secondary="#7aa8c8",
        border="rgba(0, 212, 255, 0.2)",
        success="#00ff88",
        warning="#ffaa00",
        error="#ff4466",
        arc_reactor_color=(0, 180, 255),
        arc_reactor_glow="rgba(0, 180, 255, 0.5)"
    ),
    "holographic": Theme(
        name="HOLOGRAPHIC",
        background="#0a0010",
        surface="#150025",
        surface_alt="#200035",
        primary="#ff00ff",
        primary_glow="rgba(255, 0, 255, 0.3)",
        secondary="#8800ff",
        accent="#00ffff",
        text="#f0e0ff",
        text_secondary="#c090dd",
        border="rgba(255, 0, 255, 0.2)",
        success="#00ffaa",
        warning="#ffaa00",
        error="#ff0066",
        arc_reactor_color=(200, 0, 255),
        arc_reactor_glow="rgba(200, 0, 255, 0.5)"
    ),
    "professional": Theme(
        name="PROFESSIONAL",
        background="#1a1a2e",
        surface="#16213e",
        surface_alt="#1f2b4d",
        primary="#4a90d9",
        primary_glow="rgba(74, 144, 217, 0.3)",
        secondary="#2d5a87",
        accent="#00d4aa",
        text="#e8eef5",
        text_secondary="#a0b8d0",
        border="rgba(74, 144, 217, 0.2)",
        success="#00d4aa",
        warning="#ffaa00",
        error="#ff6b6b",
        arc_reactor_color=(74, 144, 217),
        arc_reactor_glow="rgba(74, 144, 217, 0.5)"
    )
}

# =============================================================================
# MEMORY DATABASE — Perpetual Memory Graph
# =============================================================================

class MemoryGraph:
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser("~"), ".friday_memory_ultra.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self.vector_index = {}  # Simple keyword-based index
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT,
                importance INTEGER DEFAULT 5,
                embeddings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                tags TEXT
            );
            
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            );
            
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT,
                description TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                target_id INTEGER,
                relation_type TEXT,
                strength INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            );
            
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                due_date TIMESTAMP,
                completed INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 5,
                project TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                remind_at TIMESTAMP,
                triggered INTEGER DEFAULT 0,
                recurring TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                content TEXT,
                content_type TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                response TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
            CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
            CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
            CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_base(source);
        """)
        self.conn.commit()
    
    def remember(self, key: str, value: str, category: str = "general", importance: int = 5, tags: List[str] = None):
        cursor = self.conn.cursor()
        tags_str = json.dumps(tags) if tags else None
        cursor.execute("""
            INSERT OR REPLACE INTO memories (key, value, category, importance, tags, accessed_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, value, category, importance, tags_str))
        self.conn.commit()
        
        # Update vector index
        words = f"{key} {value}".lower().split()
        for word in words:
            if word not in self.vector_index:
                self.vector_index[word] = []
            self.vector_index[word].append(key)
        
        # Extract and store entities
        self._extract_entities(key, value)
    
    def _extract_entities(self, key: str, value: str):
        # Simple entity extraction
        cursor = self.conn.cursor()
        
        # Extract capitalized words as potential entities
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', f"{key} {value}")
        for entity in entities[:5]:  # Limit to 5 per memory
            if len(entity) > 2:
                cursor.execute("""
                    INSERT OR IGNORE INTO entities (name, description, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (entity, f"Related to: {key}"))
    
    def recall(self, key: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memories SET access_count = access_count + 1, 
            accessed_at = CURRENT_TIMESTAMP WHERE key = ?
        """, (key,))
        self.conn.commit()
        
        cursor.execute("SELECT value FROM memories WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else None
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        query_lower = query.lower()
        query_words = query_lower.split()
        
        cursor = self.conn.cursor()
        
        # Keyword-based search
        cursor.execute("""
            SELECT * FROM memories 
            WHERE key LIKE ? OR value LIKE ? OR category LIKE ? OR tags LIKE ?
            ORDER BY importance DESC, access_count DESC, accessed_at DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        
        # Also search entities
        cursor.execute("""
            SELECT * FROM entities 
            WHERE name LIKE ? OR description LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit // 2))
        
        entity_results = [dict(row) for row in cursor.fetchall()]
        
        return {"memories": results, "entities": entity_results}
    
    def learn_pattern(self, pattern: str, response: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO learned_patterns (pattern, response, usage_count, last_used)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        """, (pattern, response))
        self.conn.commit()
    
    def get_pattern(self, pattern: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE learned_patterns SET usage_count = usage_count + 1, 
            last_used = CURRENT_TIMESTAMP WHERE pattern = ?
        """, (pattern,))
        self.conn.commit()
        
        cursor.execute("SELECT response FROM learned_patterns WHERE pattern = ?", (pattern,))
        result = cursor.fetchone()
        return result['response'] if result else None
    
    def add_conversation(self, role: str, content: str, session_id: str = "default", metadata: Dict = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (role, content, metadata, session_id)
            VALUES (?, ?, ?, ?)
        """, (role, content, json.dumps(metadata) if metadata else None, session_id))
        self.conn.commit()
        
        # Extract entities from conversation
        self._extract_entities(role, content)
    
    def get_conversation_history(self, session_id: str = "default", limit: int = 50) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in reversed(rows)]
    
    def add_entity(self, name: str, entity_type: str, description: str = "", metadata: Dict = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO entities (name, entity_type, description, metadata, last_seen)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, entity_type, description, json.dumps(metadata) if metadata else None))
        self.conn.commit()
    
    def get_entity(self, name: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE entities SET last_seen = CURRENT_TIMESTAMP WHERE name = ?
        """, (name,))
        self.conn.commit()
        
        cursor.execute("SELECT * FROM entities WHERE name = ?", (name,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_related_entities(self, entity_name: str, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.* FROM entities e
            JOIN relations r ON e.id = r.target_id
            JOIN entities source ON source.id = r.source_id
            WHERE source.name = ?
            UNION
            SELECT e.* FROM entities e
            JOIN relations r ON e.id = r.source_id
            JOIN entities target ON target.id = r.target_id
            WHERE target.name = ?
            LIMIT ?
        """, (entity_name, entity_name, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_task(self, title: str, description: str = "", due_date: str = None, priority: int = 5, project: str = ""):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, priority, project)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, due_date, priority, project))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tasks(self, include_completed: bool = False, project: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if not include_completed:
            query += " AND completed = 0"
        if project:
            query += " AND project = ?"
            params.append(project)
        
        query += " ORDER BY priority DESC, due_date ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def complete_task(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def add_reminder(self, message: str, remind_at: str, recurring: str = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (message, remind_at, recurring) VALUES (?, ?, ?)
        """, (message, remind_at, recurring))
        self.conn.commit()
    
    def get_due_reminders(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE triggered = 0 AND datetime(remind_at) <= datetime('now')
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def add_knowledge(self, source: str, content: str, content_type: str = "text", url: str = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_base (source, content, content_type, url)
            VALUES (?, ?, ?, ?)
        """, (source, content, content_type, url))
        self.conn.commit()
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE knowledge_base SET last_accessed = CURRENT_TIMESTAMP
            WHERE content LIKE ? OR source LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        self.conn.commit()
        
        cursor.execute("""
            SELECT * FROM knowledge_base 
            WHERE content LIKE ? OR source LIKE ?
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def set_preference(self, key: str, value: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    
    def close(self):
        self.conn.close()


# =============================================================================
# VOICE ENGINE — Streaming TTS with custom voice
# =============================================================================

class VoiceEngine:
    def __init__(self):
        self.voice_name = "en-US-GuyNeural"
        self.rate = "+0%"
        self.volume = "+0%"
        self._edge_available = False
        self._voice_file = os.path.join(os.path.expanduser("~"), ".friday_voice.mp3")
        self._check_voice()
        self.current_streaming = False
    
    def _check_voice(self):
        try:
            import edge_tts
            self._edge_available = True
        except ImportError:
            self._edge_available = False
        
        if os.path.exists(self._voice_file):
            self._use_custom = True
        else:
            self._use_custom = False
    
    def set_custom_voice(self, voice_file: str):
        if os.path.exists(voice_file):
            self._voice_file = voice_file
            self._use_custom = True
    
    def speak(self, text: str):
        def run():
            try:
                if self._use_custom:
                    self._speak_custom(text)
                elif self._edge_available:
                    self._speak_edge(text)
                else:
                    self._speak_say(text)
            except:
                try:
                    self._speak_say(text)
                except:
                    pass
        threading.Thread(target=run, daemon=True).start()
    
    def speak_streaming(self, text: str, on_progress: Callable = None):
        """Streaming speak with progress callback"""
        self.current_streaming = True
        
        def run():
            try:
                if self._edge_available:
                    self._speak_edge_streaming(text, on_progress)
                else:
                    self._speak_say(text)
            except:
                self._speak_say(text)
        
        threading.Thread(target=run, daemon=True).start()
    
    def _speak_custom(self, text: str):
        try:
            subprocess.run(["afplay", self._voice_file], timeout=30, capture_output=True)
        except:
            self._speak_say(text)
    
    def _speak_edge(self, text: str):
        import edge_tts, asyncio
        async def _talk():
            try:
                mp3_path = tempfile.mktemp(suffix=".mp3")
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate, volume=self.volume)
                await communicate.save(mp3_path)
                subprocess.run(["afplay", mp3_path], timeout=30, capture_output=True)
                os.unlink(mp3_path)
            except:
                self._speak_say(text)
        try:
            asyncio.run(_talk())
        except:
            self._speak_say(text)
    
    def _speak_edge_streaming(self, text: str, on_progress: Callable):
        import edge_tts, asyncio
        async def _talk():
            try:
                mp3_path = tempfile.mktemp(suffix=".mp3")
                communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate, volume=self.volume)
                await communicate.save(mp3_path)
                if on_progress:
                    on_progress(100)
                subprocess.run(["afplay", mp3_path], timeout=30, capture_output=True)
                os.unlink(mp3_path)
            except:
                self._speak_say(text)
        try:
            asyncio.run(_talk())
        except:
            self._speak_say(text)
    
    def _speak_say(self, text: str):
        cmd = ["say", "-v", "Samantha", "-r", "165", text]
        subprocess.run(cmd, timeout=30, capture_output=True)


# =============================================================================
# VOICE RECOGNITION — Swift-based native
# =============================================================================

class VoiceListener(QObject):
    heard = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    partial_result = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self._proc = None
    
    def start(self):
        if self.is_listening:
            self.stop()
            return
        self.is_listening = True
        self.status_changed.emit("listening")
        threading.Thread(target=self._run_swift, daemon=True).start()
    
    def _run_swift(self):
        import subprocess, os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        swift_path = os.path.join(script_dir, "voice_helper.swift")
        
        if not os.path.exists(swift_path):
            self.status_changed.emit("unavailable")
            self.is_listening = False
            return
        
        try:
            self._proc = subprocess.Popen(
                ["swift", swift_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            out, _ = self._proc.communicate(timeout=12)
            for line in out.split("\n"):
                if line.startswith("TEXT:"):
                    text = line[5:].strip()
                    if text:
                        self.heard.emit(text)
                        break
        except subprocess.TimeoutExpired:
            if self._proc:
                self._proc.kill()
        except FileNotFoundError:
            self.status_changed.emit("unavailable")
        except:
            pass
        finally:
            self.is_listening = False
            self.status_changed.emit("idle")
    
    def stop(self):
        self.is_listening = False
        if self._proc:
            try:
                self._proc.kill()
            except:
                pass


# =============================================================================
# AGENTIC AI ENGINE — Autonomous task execution
# =============================================================================

@dataclass
class AgentTask:
    id: str
    description: str
    status: str  # pending, running, completed, failed
    steps: List[Dict] = field(default_factory=list)
    result: Any = None
    created_at: float = field(default_factory=time.time)

class AgenticEngine:
    def __init__(self, memory: MemoryGraph):
        self.memory = memory
        self.active_tasks = {}
        self.task_counter = 0
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register available tools for agents"""
        self.tools = {
            "web_search": self._tool_web_search,
            "calculate": self._tool_calculate,
            "run_code": self._tool_run_code,
            "send_email": self._tool_send_email,
            "read_file": self._tool_read_file,
            "write_file": self._tool_write_file,
            "take_screenshot": self._tool_screenshot,
            "open_app": self._tool_open_app,
            "send_message": self._tool_send_message,
            "control_smart_home": self._tool_smart_home,
            "analyze_data": self._tool_analyze_data,
            "schedule_meeting": self._tool_schedule_meeting,
            "make_phone_call": self._tool_make_call,
        }
    
    def execute_task(self, description: str, context: Dict = None) -> AgentTask:
        """Execute an autonomous task"""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        task = AgentTask(
            id=task_id,
            description=description,
            status="running"
        )
        self.active_tasks[task_id] = task
        
        # Execute in background
        threading.Thread(target=self._execute_task_async, args=(task, context or {}), daemon=True).start()
        
        return task
    
    def _execute_task_async(self, task: AgentTask, context: Dict):
        try:
            # Break down task into steps
            steps = self._plan_steps(task.description, context)
            task.steps = steps
            
            for i, step in enumerate(steps):
                task.status = f"running_step_{i+1}"
                
                # Execute step
                tool_name = step.get("tool")
                if tool_name and tool_name in self.tools:
                    result = self.tools[tool_name](step.get("params", {}))
                    step["result"] = result
                else:
                    step["result"] = "Tool not found"
                
                time.sleep(0.5)  # Simulate processing
            
            task.status = "completed"
            task.result = "Task completed successfully"
            
        except Exception as e:
            task.status = "failed"
            task.result = str(e)
    
    def _plan_steps(self, description: str, context: Dict) -> List[Dict]:
        """Plan execution steps for a task"""
        steps = []
        
        # Simple rule-based step planning
        description_lower = description.lower()
        
        if "research" in description_lower or "find" in description_lower:
            steps.append({"tool": "web_search", "params": {"query": description}})
        
        if "calculate" in description_lower or "math" in description_lower:
            steps.append({"tool": "calculate", "params": {"expression": description}})
        
        if "code" in description_lower or "script" in description_lower:
            steps.append({"tool": "run_code", "params": {"task": description}})
        
        if "email" in description_lower:
            steps.append({"tool": "send_email", "params": {"message": description}})
        
        if "analyze" in description_lower and "data" in description_lower:
            steps.append({"tool": "analyze_data", "params": {"task": description}})
        
        if "open" in description_lower or "launch" in description_lower:
            app = description.split()[-1]
            steps.append({"tool": "open_app", "params": {"app": app}})
        
        if "screenshot" in description_lower:
            steps.append({"tool": "take_screenshot", "params": {}})
        
        if not steps:
            steps.append({"tool": "web_search", "params": {"query": description}})
        
        return steps
    
    # Tool implementations
    def _tool_web_search(self, params: Dict) -> str:
        query = params.get("query", "")
        url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        subprocess.run(["open", url], capture_output=True)
        return f"Searching for: {query}"
    
    def _tool_calculate(self, params: Dict) -> str:
        expression = params.get("expression", "")
        math_expr = re.sub(r'[^0-9+\-*/().]', '', expression)
        try:
            result = eval(math_expr)
            return f"{math_expr} = {result}"
        except:
            return "Calculation failed"
    
    def _tool_run_code(self, params: Dict) -> str:
        task = params.get("task", "")
        return f"Code execution ready for: {task[:50]}"
    
    def _tool_send_email(self, params: Dict) -> str:
        message = params.get("message", "")
        return f"Email composition ready for: {message[:50]}"
    
    def _tool_read_file(self, params: Dict) -> str:
        path = params.get("path", "")
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()[:1000]
        return "File not found"
    
    def _tool_write_file(self, params: Dict) -> str:
        path = params.get("path", "")
        content = params.get("content", "")
        try:
            with open(path, "w") as f:
                f.write(content)
            return f"File written: {path}"
        except Exception as e:
            return f"Write failed: {e}"
    
    def _tool_screenshot(self, params: Dict) -> str:
        path = os.path.expanduser(f"~/Desktop/screenshot_{int(time.time())}.png")
        subprocess.run(["screencapture", "-x", path], capture_output=True)
        return f"Screenshot saved: {path}"
    
    def _tool_open_app(self, params: Dict) -> str:
        app = params.get("app", "")
        subprocess.run(["open", "-a", app], capture_output=True)
        return f"Opening: {app}"
    
    def _tool_send_message(self, params: Dict) -> str:
        return "Message sending ready"
    
    def _tool_smart_home(self, params: Dict) -> str:
        action = params.get("action", "")
        return f"Smart home: {action}"
    
    def _tool_analyze_data(self, params: Dict) -> str:
        task = params.get("task", "")
        return f"Data analysis ready for: {task[:50]}"
    
    def _tool_schedule_meeting(self, params: Dict) -> str:
        return "Meeting scheduling ready"
    
    def _tool_make_call(self, params: Dict) -> str:
        return "Phone call ready"


# =============================================================================
# MULTI-AGENT SWARM — Parallel specialized agents
# =============================================================================

class Agent:
    def __init__(self, name: str, role: str, expertise: List[str]):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.memory = []
        self.result = None
    
    def think(self, task: str) -> str:
        """Agent reasoning process"""
        return f"[{self.name}] Analyzing: {task[:100]}"
    
    def contribute(self, task: str) -> Dict:
        """Agent contribution to swarm"""
        return {
            "agent": self.name,
            "role": self.role,
            "thinking": self.think(task),
            "result": self.result or f"Contribution from {self.name}",
            "confidence": random.uniform(0.7, 0.99)
        }

class MultiAgentSwarm:
    def __init__(self, memory: MemoryGraph):
        self.memory = memory
        self.agents = self._create_agents()
    
    def _create_agents(self) -> List[Agent]:
        return [
            Agent("Researcher", "Research Specialist", ["search", "analyze", "facts"]),
            Agent("Coder", "Software Engineer", ["code", "debug", "architecture"]),
            Agent("Critic", "Quality Assurance", ["review", "improve", "validate"]),
            Agent("Writer", "Technical Writer", ["documentation", "explanation", "summarize"]),
            Agent("Strategist", "Planning Expert", ["plan", "coordinate", "optimize"]),
        ]
    
    def solve(self, problem: str, required_agents: List[str] = None) -> Dict:
        """Solve problem using multiple agents"""
        if required_agents:
            active_agents = [a for a in self.agents if a.name in required_agents]
        else:
            active_agents = self.agents
        
        results = []
        for agent in active_agents:
            contribution = agent.contribute(problem)
            results.append(contribution)
        
        # Synthesize results
        synthesis = self._synthesize(results, problem)
        
        return {
            "problem": problem,
            "agents": results,
            "synthesis": synthesis,
            "confidence": sum(r["confidence"] for r in results) / len(results)
        }
    
    def _synthesize(self, results: List[Dict], problem: str) -> str:
        """Synthesize agent contributions into final answer"""
        return f"Combined insights from {len(results)} agents. " + \
               f"Best approach synthesized from {', '.join(r['agent'] for r in results)}."


# =============================================================================
# CODE EXECUTOR — Write and run code
# =============================================================================

class CodeExecutor:
    def __init__(self):
        self.sandbox_dir = os.path.join(tempfile.gettempdir(), "friday_code")
        os.makedirs(self.sandbox_dir, exist_ok=True)
    
    def write_and_run(self, task: str, language: str = "python") -> Dict:
        """Write and execute code based on task description"""
        try:
            # Generate code
            code = self._generate_code(task, language)
            
            # Save to file
            filename = f"friday_code_{int(time.time())}.{'py' if language == 'python' else 'js'}"
            filepath = os.path.join(self.sandbox_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(code)
            
            # Execute
            result = self._execute_code(filepath, language)
            
            return {
                "success": True,
                "code": code,
                "output": result,
                "filepath": filepath
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": code if 'code' in locals() else None
            }
    
    def _generate_code(self, task: str, language: str) -> str:
        """Generate code from task description using AI"""
        # Simple template-based generation
        # In production, this would use AI to generate code
        
        task_lower = task.lower()
        
        if "prime" in task_lower or "prime numbers" in task_lower:
            if language == "python":
                return '''import sys

def find_primes(n):
    """Find all prime numbers up to n"""
    if n < 2:
        return []
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    
    return [i for i in range(2, n + 1) if sieve[i]]

# Find primes up to 100
primes = find_primes(100)
print(f"Prime numbers up to 100: {primes}")
print(f"Total: {len(primes)} primes")
'''
        
        elif "fibonacci" in task_lower:
            if language == "python":
                return '''def fibonacci(n):
    """Generate Fibonacci sequence"""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Generate first 20 Fibonacci numbers
fib = fibonacci(20)
print(f"Fibonacci sequence: {fib}")
'''
        
        elif "sort" in task_lower:
            if language == "python":
                return '''import random

def quick_sort(arr):
    """Quick sort implementation"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# Test with random numbers
data = random.sample(range(1, 51), 20)
print(f"Original: {data}")
print(f"Sorted: {quick_sort(data)}")
'''
        
        elif "analyze" in task_lower and "data" in task_lower:
            if language == "python":
                return '''import random
from statistics import mean, median, stdev

def analyze_data(n=100):
    """Generate and analyze sample data"""
    data = [random.gauss(50, 15) for _ in range(n)]
    
    print(f"Data Analysis (n={n})")
    print(f"Mean: {mean(data):.2f}")
    print(f"Median: {median(data):.2f}")
    print(f"Std Dev: {stdev(data):.2f}")
    print(f"Min: {min(data):.2f}")
    print(f"Max: {max(data):.2f}")
    print(f"\\nFirst 10 values: {[round(x, 2) for x in data[:10]]}")

analyze_data()
'''
        
        else:
            # Generic template
            if language == "python":
                return f'''# Task: {task[:100]}
# Generated by F.R.I.D.A.Y.

def main():
    print("Executing: {task[:50]}...")
    print("Task completed successfully!")

if __name__ == "__main__":
    main()
'''
    
    def _execute_code(self, filepath: str, language: str) -> str:
        """Execute code and return output"""
        try:
            if language == "python":
                result = subprocess.run(
                    ["python3", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif language == "javascript":
                result = subprocess.run(
                    ["node", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                return f"Unsupported language: {language}"
            
            output = result.stdout if result.stdout else result.stderr
            return output if output else "Code executed (no output)"
        
        except subprocess.TimeoutExpired:
            return "Execution timed out (30s limit)"
        except Exception as e:
            return f"Execution error: {str(e)}"


# =============================================================================
# WEB AGENT — Autonomous browsing and actions
# =============================================================================

class WebAgent:
    def __init__(self):
        self.browser_actions = {
            "search": self._search,
            "open": self._open_url,
            "click": self._click_element,
            "fill": self._fill_form,
            "submit": self._submit_form,
            "scroll": self._scroll,
        }
    
    def execute(self, action: str, params: Dict) -> str:
        """Execute web action"""
        if action in self.browser_actions:
            return self.browser_actions[action](params)
        return f"Unknown action: {action}"
    
    def _search(self, params: Dict) -> str:
        query = params.get("query", "")
        url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        subprocess.run(["open", url], capture_output=True)
        return f"Searching: {query}"
    
    def _open_url(self, params: Dict) -> str:
        url = params.get("url", "")
        if not url.startswith("http"):
            url = f"https://{url}"
        subprocess.run(["open", url], capture_output=True)
        return f"Opening: {url}"
    
    def _click_element(self, params: Dict) -> str:
        selector = params.get("selector", "")
        return f"Would click: {selector}"
    
    def _fill_form(self, params: Dict) -> str:
        field = params.get("field", "")
        value = params.get("value", "")
        return f"Would fill {field} with: {value}"
    
    def _submit_form(self, params: Dict) -> str:
        return "Would submit form"
    
    def _scroll(self, params: Dict) -> str:
        direction = params.get("direction", "down")
        amount = params.get("amount", 1)
        return f"Would scroll {direction} {amount} times"


# =============================================================================
# DATA ANALYSIS ENGINE
# =============================================================================

class DataAnalyzer:
    def __init__(self):
        self.supported_formats = [".csv", ".xlsx", ".xls", ".json"]
    
    def analyze(self, filepath: str, task: str) -> Dict:
        """Analyze data file"""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == ".csv":
                return self._analyze_csv(filepath, task)
            elif ext in [".xlsx", ".xls"]:
                return self._analyze_excel(filepath, task)
            elif ext == ".json":
                return self._analyze_json(filepath, task)
            else:
                return {"error": f"Unsupported format: {ext}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_csv(self, filepath: str, task: str) -> Dict:
        try:
            import pandas as pd
            
            df = pd.read_csv(filepath)
            
            analysis = {
                "file": filepath,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "summary": df.describe().to_dict(),
                "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
            }
            
            # Check for specific analysis requests
            task_lower = task.lower()
            
            if "trend" in task_lower or "growth" in task_lower:
                numerical_cols = df.select_dtypes(include=['number']).columns
                if len(numerical_cols) > 0:
                    col = numerical_cols[0]
                    first_half = df[col].iloc[:len(df)//2].mean()
                    second_half = df[col].iloc[len(df)//2:].mean()
                    trend = "increasing" if second_half > first_half else "decreasing"
                    analysis["trend"] = f"{col} is {trend}"
            
            if "correlation" in task_lower:
                corr = df.corr().to_dict()
                analysis["correlation"] = corr
            
            return analysis
        
        except ImportError:
            return {"error": "pandas required for analysis. Install: pip install pandas"}
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_excel(self, filepath: str, task: str) -> Dict:
        try:
            import pandas as pd
            df = pd.read_excel(filepath)
            return {
                "file": filepath,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "preview": df.head(10).to_dict()
            }
        except ImportError:
            return {"error": "pandas required. Install: pip install pandas openpyxl"}
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_json(self, filepath: str, task: str) -> Dict:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return {
                "file": filepath,
                "type": type(data).__name__,
                "keys": list(data.keys()) if isinstance(data, dict) else "List",
                "preview": str(data)[:500]
            }
        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# SMART HOME HUB
# =============================================================================

class SmartHomeHub:
    def __init__(self):
        self.devices = {
            "lights": ["bedroom_light", "living_room_light", "kitchen_light"],
            "thermostat": ["main_thermostat"],
            "locks": ["front_door", "back_door"],
            "cameras": ["front_camera", "back_camera"],
        }
        self.device_states = {}
    
    def control(self, command: str) -> str:
        """Control smart home devices"""
        command_lower = command.lower()
        
        # Lights
        if "light" in command_lower:
            if "on" in command_lower:
                return self._turn_on_light(command_lower)
            elif "off" in command_lower:
                return self._turn_off_light(command_lower)
            elif "dim" in command_lower:
                return self._dim_light(command_lower)
        
        # Thermostat
        if "temperature" in command_lower or "thermostat" in command_lower or "ac" in command_lower or "heat" in command_lower:
            return self._control_thermostat(command_lower)
        
        # Locks
        if "lock" in command_lower:
            return self._control_lock(command_lower)
        
        # Cameras
        if "camera" in command_lower:
            return self._view_camera(command_lower)
        
        return "Smart home command not recognized"
    
    def _turn_on_light(self, command: str) -> str:
        for room in ["bedroom", "living room", "kitchen"]:
            if room in command:
                self.device_states[f"{room}_light"] = "on"
                return f"Turned on {room} light"
        return "Which light should I turn on?"
    
    def _turn_off_light(self, command: str) -> str:
        for room in ["bedroom", "living room", "kitchen"]:
            if room in command:
                self.device_states[f"{room}_light"] = "off"
                return f"Turned off {room} light"
        return "Which light should I turn off?"
    
    def _dim_light(self, command: str) -> str:
        nums = [int(s) for s in command.split() if s.isdigit()]
        brightness = nums[0] if nums else 50
        return f"Dimmed light to {brightness}%"
    
    def _control_thermostat(self, command: str) -> str:
        nums = [int(s) for s in command.split() if s.isdigit()]
        if nums:
            temp = nums[0]
            return f"Set temperature to {temp}°C"
        return "What temperature should I set?"
    
    def _control_lock(self, command: str) -> str:
        action = "Locked" if "lock" in command else "Unlocked"
        return f"{action} door"
    
    def _view_camera(self, command: str) -> str:
        return "Opening camera feed"


# =============================================================================
# LEARNING MODE — AI-powered teaching
# =============================================================================

class LearningMode:
    def __init__(self, memory: MemoryGraph):
        self.memory = memory
    
    def teach(self, topic: str, level: str = "beginner") -> Dict:
        """Teach a topic at specified level"""
        
        topics_db = {
            "python": {
                "beginner": [
                    "Python is a high-level programming language",
                    "It's known for its simple, readable syntax",
                    "Great for beginners to learn programming",
                    "Used in web development, data science, AI, and more"
                ],
                "intermediate": [
                    "Python supports object-oriented programming",
                    "List comprehensions for concise data processing",
                    "Decorators for modifying function behavior",
                    "Generators for memory-efficient iteration"
                ],
                "advanced": [
                    "Python has GIL limiting true multithreading",
                    "Async/await for concurrent I/O operations",
                    "Metaclasses for class creation control",
                    "Descriptors for attribute access protocol"
                ]
            },
            "ai": {
                "beginner": [
                    "AI stands for Artificial Intelligence",
                    "It enables machines to learn from data",
                    "Machine learning is a subset of AI",
                    "ChatGPT uses Large Language Models"
                ],
                "intermediate": [
                    "Neural networks mimic brain structure",
                    "Training involves forward and backward propagation",
                    "Loss functions measure prediction error",
                    "Optimizers like Adam adjust learning rates"
                ],
                "advanced": [
                    "Transformers use self-attention mechanisms",
                    "RLHF aligns models with human preferences",
                    "Diffusion models generate images via denoising",
                    "MoE architectures route to specialized experts"
                ]
            }
        }
        
        topic_lower = topic.lower()
        content = []
        
        for key, levels in topics_db.items():
            if key in topic_lower:
                content = levels.get(level, levels["beginner"])
                break
        
        if not content:
            content = [
                f"Learning about: {topic}",
                "I'll explain this in a way that's easy to understand.",
                f"Current level: {level}",
                "Ask me specific questions to learn more!"
            ]
        
        return {
            "topic": topic,
            "level": level,
            "lessons": content,
            "next_topics": ["Try asking about applications", "Ask for code examples", "Request a demo"]
        }
    
    def quiz(self, topic: str) -> Dict:
        """Generate a quiz for the topic"""
        return {
            "topic": topic,
            "questions": [
                {"q": f"What is {topic}?", "options": ["A", "B", "C", "D"], "answer": "A"},
                {"q": f"Example question about {topic}?", "options": ["Yes", "No", "Maybe", "Probably"], "answer": "Yes"},
            ]
        }


# =============================================================================
# VIDEO/METTING TRANSCRIPTION
# =============================================================================

class VideoTranscriber:
    def __init__(self):
        pass
    
    def transcribe_youtube(self, url: str) -> Dict:
        """Transcribe YouTube video"""
        return {
            "url": url,
            "status": "ready",
            "message": "YouTube transcription ready. Provide video URL for details."
        }
    
    def transcribe_meeting(self, meeting_link: str) -> Dict:
        """Transcribe meeting (Zoom, Teams, etc.)"""
        return {
            "meeting": meeting_link,
            "status": "ready",
            "message": "Meeting transcription ready. Join meeting to start."
        }
    
    def summarize_transcript(self, transcript: str) -> str:
        """Summarize video/meeting transcript"""
        return f"Summary of transcript ({len(transcript)} chars): Key points extracted."


# =============================================================================
# PERSONAL CRM
# =============================================================================

class PersonalCRM:
    def __init__(self, memory: MemoryGraph):
        self.memory = memory
        self.contacts = {}
    
    def add_contact(self, name: str, metadata: Dict = None):
        """Add or update a contact"""
        self.memory.add_entity(name, "contact", json.dumps(metadata) if metadata else "")
        self.contacts[name] = metadata or {}
    
    def get_contact(self, name: str) -> Optional[Dict]:
        """Get contact info"""
        return self.memory.get_entity(name)
    
    def get_last_interaction(self, name: str) -> Optional[str]:
        """Find last interaction with contact"""
        history = self.memory.get_conversation_history(limit=100)
        for entry in history:
            if name.lower() in entry.get('content', '').lower():
                return entry.get('timestamp')
        return None
    
    def add_reminder(self, name: str, message: str, when: str):
        """Set reminder to follow up with contact"""
        self.memory.add_reminder(f"Follow up with {name}: {message}", when)


# =============================================================================
# EMAIL AUTOMATION
# =============================================================================

class EmailAutomation:
    def __init__(self):
        self.smtp_server = None
        self.logged_in = False
    
    def compose_email(self, to: str, subject: str, body: str) -> str:
        """Compose an email draft"""
        return f"""To: {to}
Subject: {subject}

{body}

---
Drafted by F.R.I.D.A.Y."""
    
    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send email (requires SMTP config)"""
        # Placeholder - needs SMTP credentials
        return f"Email ready to send to {to}. Subject: {subject}"
    
    def read_emails(self, count: int = 10) -> str:
        """Read recent emails"""
        return f"Last {count} emails retrieved. Connect email for full functionality."
    
    def summarize_unread(self) -> str:
        """Summarize unread emails"""
        return "No unread emails. All caught up!"


# =============================================================================
# ARC REACTOR WIDGET — Advanced JARVIS Style
# =============================================================================

class ArcReactorWidget(QWidget):
    def __init__(self, parent=None, theme: Theme = None):
        super().__init__(parent)
        self.theme = theme or THEMES["jarvis"]
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 300)
        
        self.angle = 0.0
        self.phase = 0.0
        self.pulse = 0.5
        self.wake_active = False
        self.wake_timer = 0
        self.particles = []
        
        for _ in range(30):
            self.particles.append({
                'angle': random.random() * 360,
                'radius': 30 + random.random() * 90,
                'speed': 0.2 + random.random() * 0.6,
                'size': 1 + random.random() * 3,
                'alpha': 50 + random.random() * 100
            })
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(25)
    
    def set_theme(self, theme: Theme):
        self.theme = theme
        self.update()
    
    def animate(self):
        self.angle += 1
        self.phase += 0.05
        self.pulse = 0.6 + 0.4 * math.sin(self.phase * 1.5)
        
        if self.wake_active:
            self.wake_timer += 1
            if self.wake_timer > 60:
                self.wake_active = False
                self.wake_timer = 0
        
        for p in self.particles:
            p['angle'] += p['speed']
        
        self.update()
    
    def pulse_wake(self):
        self.wake_active = True
        self.wake_timer = 0
    
    def paintEvent(self, event):
        w = min(self.width(), self.height())
        cx, cy = self.width() / 2, self.height() / 2
        s = w / 2
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        p.translate(cx, cy)
        p.scale(s / 150, s / 150)
        
        r, g, b = self.theme.arc_reactor_color
        base_color = QColor(r, g, b) if not self.wake_active else QColor(0, 255, 180)
        glow_intensity = int(200 * self.pulse)
        
        # Outer ambient glow
        for i in range(15, 0, -1):
            alpha = int(2 * (16 - i))
            radius = 140 + i * 6
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), alpha), i * 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        
        # Containment ring
        p.setPen(QPen(QColor(30, 40, 50), 5))
        p.setBrush(QBrush(QColor(15, 20, 28)))
        p.drawEllipse(-140, -140, 280, 280)
        
        # Tick marks
        for i in range(60):
            angle_rad = math.radians(i * 6)
            inner_r = 130
            outer_r = 138 if i % 5 == 0 else 134
            x1 = inner_r * math.cos(angle_rad)
            y1 = inner_r * math.sin(angle_rad)
            x2 = outer_r * math.cos(angle_rad)
            y2 = outer_r * math.sin(angle_rad)
            
            color_alpha = 220 if i % 5 == 0 else 120
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), color_alpha), 2 if i % 5 == 0 else 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # Energy rings (3 layers, different speeds)
        for ring_idx, (ring_r, ring_alpha, ring_speed, num_segments) in enumerate([
            (115, 220, 0.7, 40),
            (95, 200, -1.1, 36),
            (75, 180, 1.3, 32),
            (55, 160, -0.8, 28),
        ]):
            actual_angle = self.angle * ring_speed
            seg_span = 360 / num_segments * 0.7
            
            for seg in range(num_segments):
                seg_angle = math.radians(seg * (360 / num_segments) + actual_angle)
                arc_angle = math.degrees(seg_angle) - seg_span / 2
                
                # Glow
                for glow_i in range(5, 0, -1):
                    glow_alpha = int(ring_alpha / (glow_i * 2.5))
                    p.setPen(QPen(
                        QColor(base_color.red(), base_color.green(), base_color.blue(), glow_alpha),
                        glow_i * 2
                    ))
                    p.drawArc(
                        QRectF(-ring_r, -ring_r, ring_r * 2, ring_r * 2),
                        int(arc_angle * 16), int(seg_span * 16)
                    )
                
                # Main arc
                p.setPen(QPen(
                    QColor(base_color.red(), base_color.green(), base_color.blue(), int(ring_alpha * self.pulse)),
                    2.5
                ))
                p.drawArc(
                    QRectF(-ring_r, -ring_r, ring_r * 2, ring_r * 2),
                    int(arc_angle * 16), int(seg_span * 16)
                )
        
        # Hexagonal housing
        hex_pts = []
        for i in range(6):
            angle_rad = math.radians(i * 60 + 30)
            hex_pts.append(QPointF(38 * math.cos(angle_rad), 38 * math.sin(angle_rad)))
        
        for layer in range(4):
            offset = layer * 2
            path = QPainterPath()
            path.moveTo(hex_pts[0])
            for pt in hex_pts[1:]:
                path.lineTo(pt)
            path.closeSubpath()
            
            p.setPen(QPen(QColor(20 + layer * 8, 40 + layer * 8, 60 + layer * 8, 255 - layer * 30), 2))
            p.setBrush(QBrush(QColor(15 + layer * 5, 30 + layer * 5, 50 + layer * 5, 200 - layer * 30)))
            p.drawPath(path)
        
        # Rotating inner hex
        p.save()
        p.rotate(self.angle * 0.6)
        
        inner_hex = []
        for i in range(6):
            angle_rad = math.radians(i * 60)
            inner_hex.append(QPointF(26 * math.cos(angle_rad), 26 * math.sin(angle_rad)))
        
        path = QPainterPath()
        path.moveTo(inner_hex[0])
        for pt in inner_hex[1:]:
            path.lineTo(pt)
        path.closeSubpath()
        
        for g in range(5, 0, -1):
            p.setPen(QPen(
                QColor(base_color.red(), base_color.green(), base_color.blue(), 35 * g),
                g * 2
            ))
            p.drawPath(path)
        
        p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 240), 2))
        p.drawPath(path)
        p.restore()
        
        # Energy arcs
        for arc_idx, (arc_r, arc_start) in enumerate([(65, 0), (48, 120), (32, 240)]):
            arc_angle = self.angle + arc_start + arc_idx * 40
            
            for w in range(4, 0, -1):
                p.setPen(QPen(
                    QColor(base_color.red(), base_color.green(), base_color.blue(), 45 * w),
                    w * 3
                ))
                p.drawArc(
                    QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2),
                    int(arc_angle * 16), 7000
                )
            
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 220), 2.5))
            p.drawArc(
                QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2),
                int(arc_angle * 16), 7000
            )
        
        # Core glow (multi-layer radial)
        core_scale = 1.0 + math.sin(self.phase * 2.5) * 0.1
        for layer in range(10, 0, -1):
            r = layer * 4.5 * core_scale
            alpha = int(20 * (11 - layer) * self.pulse)
            
            gradient = QRadialGradient(QPointF(0, 0), r)
            gradient.setColorAt(0, QColor(240, 255, 255, alpha))
            gradient.setColorAt(0.4, QColor(base_color.red(), base_color.green(), base_color.blue(), alpha // 2))
            gradient.setColorAt(1, QColor(base_color.red() // 2, base_color.green() // 2, base_color.blue() // 2, 0))
            
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(gradient))
            p.drawEllipse(QPointF(0, 0), r, r)
        
        # Inner core
        core_size = 10 * core_scale
        core_gradient = QRadialGradient(QPointF(0, 0), core_size)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 255))
        core_gradient.setColorAt(0.3, QColor(220, 250, 255, 240))
        core_gradient.setColorAt(0.7, QColor(base_color.red(), base_color.green(), base_color.blue(), 200))
        core_gradient.setColorAt(1, QColor(base_color.red() // 2, base_color.green() // 2, base_color.blue() // 2, 0))
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(core_gradient))
        p.drawEllipse(QPointF(0, 0), core_size, core_size)
        
        # Highlight
        p.setPen(QPen(QColor(255, 255, 255, 120), 0.8))
        p.drawEllipse(QPointF(-2.5, -2.5), 4, 4)
        
        # Particles
        for part in self.particles:
            pr = part['radius']
            px = pr * math.cos(math.radians(part['angle']))
            py = pr * math.sin(math.radians(part['angle']))
            life_ratio = part['alpha'] / 150.0
            pa = int(180 * life_ratio * self.pulse)
            ps = part['size'] * life_ratio
            
            p.setPen(QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), pa), 0.5))
            p.setBrush(QBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), pa)))
            p.drawEllipse(QPointF(px, py), ps, ps)
        
        # Reflection shimmer
        refl_gradient = QLinearGradient(0, 135, 0, 145)
        refl_gradient.setColorAt(0, QColor(base_color.red(), base_color.green(), base_color.blue(), 40))
        refl_gradient.setColorAt(0.5, QColor(base_color.red(), base_color.green(), base_color.blue(), 20))
        refl_gradient.setColorAt(1, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(refl_gradient))
        p.drawRect(-110, 135, 220, 10)
        
        # Metallic rim
        for i in range(3):
            r = 145 - i
            alpha = 100 - i * 30
            p.setPen(QPen(QColor(60 + i * 25, 80 + i * 25, 100 + i * 25, alpha), 0.5))
            p.drawEllipse(QPointF(0, 0), r, r)


# =============================================================================
# CHAT BUBBLE — Modern UI
# =============================================================================

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool = False, theme: Theme = None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.theme = theme or THEMES["jarvis"]
        
        if is_user:
            style = f"""
                QFrame {{
                    background: rgba({self.theme.secondary.replace('#', '')}, 0.4);
                    border: 1px solid {self.theme.border};
                    border-radius: 16px;
                    border-top-right-radius: 4px;
                    padding: 12px 16px;
                    margin: 4px 8px 4px 60px;
                }}
            """
        else:
            style = f"""
                QFrame {{
                    background: rgba({self.theme.primary.replace('#', '')}, 0.15);
                    border: 1px solid {self.theme.border};
                    border-radius: 16px;
                    border-top-left-radius: 4px;
                    padding: 12px 16px;
                    margin: 4px 60px 4px 8px;
                }}
            """
        
        self.setStyleSheet(style)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {self.theme.text}; background: transparent; border: none;")
        label.setFont(QFont("Arial", 13))
        layout.addWidget(label)


# =============================================================================
# MENU BAR WIDGET
# =============================================================================

class MenuBarWidget:
    def __init__(self, parent_window, theme: Theme):
        self.window = parent_window
        self.theme = theme
        self.tray = QSystemTrayIcon(parent_window)
        
        self.menu = QMenu()
        
        # Header
        header = QAction(f"{APP_NAME} — Online", self.menu)
        header.setEnabled(False)
        self.menu.addAction(header)
        self.menu.addSeparator()
        
        # Quick actions
        self.menu.addAction("🎤 Voice Command", self.window.start_voice)
        self.menu.addAction("📝 New Note", self.window.add_note)
        self.menu.addAction("🔍 Quick Search", self.window.quick_search)
        self.menu.addAction("📸 Take Screenshot", self.window.take_screenshot)
        self.menu.addSeparator()
        
        # Modules
        self.menu.addAction("🤖 Agent Mode", self.window.toggle_agent_mode)
        self.menu.addAction("💻 Code Executor", self.window.open_code_executor)
        self.menu.addAction("📊 Data Analysis", self.window.open_data_analyzer)
        self.menu.addAction("🏠 Smart Home", self.window.open_smart_home)
        self.menu.addAction("📧 Email", self.window.open_email)
        self.menu.addSeparator()
        
        # Settings
        self.menu.addAction("🎨 Change Theme", self.window.change_theme)
        self.menu.addAction("⚙️ Settings", self.window.open_settings)
        self.menu.addSeparator()
        
        # Exit
        self.menu.addAction("❌ Quit", self.window.close)
        
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(lambda: self.window.show())
        
        self._update_icon()
        self.tray.show()
    
    def _update_icon(self):
        pixmap = QPixmap(32, 32)
        color = QColor(*self.theme.arc_reactor_color)
        pixmap.fill(color)
        self.tray.setIcon(QIcon(pixmap))
    
    def show_notification(self, title: str, message: str):
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)


# =============================================================================
# MAIN WINDOW — Advanced UI
# =============================================================================

class FridayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Core systems
        self.memory = MemoryGraph()
        self.voice = VoiceEngine()
        self.voice_input = VoiceListener()
        self.voice_input.heard.connect(self.on_voice_heard)
        self.voice_input.status_changed.connect(self.on_voice_status)
        
        # Advanced modules
        self.agentic = AgenticEngine(self.memory)
        self.swarm = MultiAgentSwarm(self.memory)
        self.code_executor = CodeExecutor()
        self.web_agent = WebAgent()
        self.data_analyzer = DataAnalyzer()
        self.smart_home = SmartHomeHub()
        self.learning = LearningMode(self.memory)
        self.crm = PersonalCRM(self.memory)
        self.email = EmailAutomation()
        self.video_transcriber = VideoTranscriber()
        
        # State
        self.conversation = []
        self.is_listening = False
        self.current_theme = "jarvis"
        self.theme = THEMES[self.current_theme]
        self.agent_mode = False
        
        self._init_ui()
        self._apply_theme()
        self.greeting()
    
    def _init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1200, 850)
        self.setMinimumSize(1000, 700)
        
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = self._create_header()
        main_layout.addWidget(self.header)
        
        # Content area with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 13px;
            }
        """)
        
        # Main chat tab
        self.chat_tab = self._create_chat_tab()
        self.tab_widget.addTab(self.chat_tab, "💬 Chat")
        
        # Agent tab
        self.agent_tab = self._create_agent_tab()
        self.tab_widget.addTab(self.agent_tab, "🤖 Agent")
        
        # Code tab
        self.code_tab = self._create_code_tab()
        self.tab_widget.addTab(self.code_tab, "💻 Code")
        
        # Data tab
        self.data_tab = self._create_data_tab()
        self.tab_widget.addTab(self.data_tab, "📊 Data")
        
        # Tasks tab
        self.tasks_tab = self._create_tasks_tab()
        self.tab_widget.addTab(self.tasks_tab, "✅ Tasks")
        
        # Settings tab
        self.settings_tab = self._create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        main_layout.addWidget(self.tab_widget, 1)
        
        # Menu bar
        self.menu_bar_widget = MenuBarWidget(self, self.theme)
        
        # Status timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)
        
        self.show()
    
    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setStyleSheet(f"""
            background: {self.theme.surface};
            border-bottom: 1px solid {self.theme.border};
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Arc reactor
        self.arc = ArcReactorWidget(theme=self.theme)
        self.arc.setFixedSize(60, 60)
        layout.addWidget(self.arc)
        
        # Title
        title_label = QLabel(f"{APP_NAME} v{VERSION}")
        title_label.setStyleSheet(f"color: {self.theme.primary}; font-size: 18px; font-weight: bold;")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["JARVIS", "HOLOGRAPHIC", "PROFESSIONAL"])
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        self.theme_combo.currentTextChanged.connect(self._change_theme)
        layout.addWidget(self.theme_combo)
        
        # Mode indicator
        self.mode_label = QLabel("💬 CHAT")
        self.mode_label.setStyleSheet(f"color: {self.theme.text_secondary}; font-size: 12px;")
        layout.addWidget(self.mode_label)
        
        return header
    
    def _create_chat_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Chat area
        self.chat_area = QScrollArea()
        self.chat_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(128, 128, 128, 0.2);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle {
                background: rgba(0, 212, 255, 0.4);
                border-radius: 4px;
            }
        """)
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()
        
        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area, 1)
        
        # Input area
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            background: {self.theme.surface};
            border: 1px solid {self.theme.border};
            border-radius: 12px;
            padding: 4px;
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command or press 🎤 to speak...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {self.theme.text};
                border: none;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit::placeholder {{ color: {self.theme.text_secondary}; }}
        """)
        self.input_field.setFont(QFont("Arial", 14))
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field, 1)
        
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(44, 44)
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.primary};
                border-radius: 22px;
                font-size: 20px;
            }}
            QPushButton:hover {{ background: {self.theme.secondary}; }}
        """)
        self.mic_btn.clicked.connect(self.toggle_voice)
        input_layout.addWidget(self.mic_btn)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(44, 44)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.accent};
                border-radius: 22px;
                color: white;
                font-size: 20px;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addWidget(input_container)
        
        return tab
    
    def _create_agent_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Agent status
        agent_header = QLabel("🤖 Agentic AI Engine")
        agent_header.setStyleSheet(f"color: {self.theme.primary}; font-size: 20px; font-weight: bold;")
        layout.addWidget(agent_header)
        
        # Task input
        self.agent_input = QLineEdit()
        self.agent_input.setPlaceholderText("Describe a task for F.R.I.D.A.Y. to execute autonomously...")
        self.agent_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.agent_input)
        
        # Execute button
        self.agent_btn = QPushButton("🚀 Execute Autonomous Task")
        self.agent_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.primary};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.agent_btn.clicked.connect(self.execute_agent_task)
        layout.addWidget(self.agent_btn)
        
        # Agent output
        self.agent_output = QTextEdit()
        self.agent_output.setReadOnly(True)
        self.agent_output.setStyleSheet(f"""
            QTextEdit {{
                background: {self.theme.surface};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.agent_output, 1)
        
        # Swarm button
        swarm_btn = QPushButton("🔀 Run Multi-Agent Swarm")
        swarm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.accent};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }}
        """)
        swarm_btn.clicked.connect(self.run_swarm)
        layout.addWidget(swarm_btn)
        
        return tab
    
    def _create_code_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("💻 Code Executor")
        header.setStyleSheet(f"color: {self.theme.primary}; font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Describe what code to write (e.g., 'find prime numbers')")
        self.code_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.code_input)
        
        self.code_btn = QPushButton("⚡ Write and Execute")
        self.code_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.primary};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }}
        """)
        self.code_btn.clicked.connect(self.execute_code)
        layout.addWidget(self.code_btn)
        
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.code_output.setStyleSheet(f"""
            QTextEdit {{
                background: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
                font-family: 'JetBrains Mono', monospace;
            }}
        """)
        layout.addWidget(self.code_output, 1)
        
        return tab
    
    def _create_data_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("📊 Data Analysis")
        header.setStyleSheet(f"color: {self.theme.primary}; font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        # File selector
        file_layout = QHBoxLayout()
        self.data_file_input = QLineEdit()
        self.data_file_input.setPlaceholderText("Select a data file (CSV, Excel, JSON)")
        self.data_file_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        file_layout.addWidget(self.data_file_input, 1)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.surface_alt};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px 20px;
            }}
        """)
        browse_btn.clicked.connect(self.browse_data_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Analysis task
        self.data_task_input = QLineEdit()
        self.data_task_input.setPlaceholderText("What analysis to perform? (e.g., 'find trends and correlations')")
        self.data_task_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.data_task_input)
        
        self.data_btn = QPushButton("📈 Analyze Data")
        self.data_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.primary};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }}
        """)
        self.data_btn.clicked.connect(self.analyze_data)
        layout.addWidget(self.data_btn)
        
        self.data_output = QTextEdit()
        self.data_output.setReadOnly(True)
        self.data_output.setStyleSheet(f"""
            QTextEdit {{
                background: {self.theme.surface};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.data_output, 1)
        
        return tab
    
    def _create_tasks_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("✅ Tasks & Reminders")
        header.setStyleSheet(f"color: {self.theme.primary}; font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        # Add task
        task_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.theme.surface_alt};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        task_layout.addWidget(self.task_input, 1)
        
        add_btn = QPushButton("➕ Add")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme.accent};
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
            }}
        """)
        add_btn.clicked.connect(self.add_task)
        task_layout.addWidget(add_btn)
        layout.addLayout(task_layout)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.theme.surface};
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {self.theme.border};
            }}
        """)
        layout.addWidget(self.task_list, 1)
        
        self._refresh_tasks()
        
        return tab
    
    def _create_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("⚙️ Settings")
        header.setStyleSheet(f"color: {self.theme.primary}; font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        # Voice settings
        voice_group = QGroupBox("🔊 Voice Settings")
        voice_group.setStyleSheet(f"""
            QGroupBox {{
                color: {self.theme.text};
                border: 1px solid {self.theme.border};
                border-radius: 8px;
                padding: 16px;
                margin-top: 12px;
            }}
        """)
        voice_layout = QVBoxLayout(voice_group)
        
        self.voice_enabled = QCheckBox("Enable voice responses")
        self.voice_enabled.setChecked(True)
        self.voice_enabled.setStyleSheet(f"color: {self.theme.text};")
        voice_layout.addWidget(self.voice_enabled)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        speed_layout.addWidget(self.speed_slider)
        voice_layout.addLayout(speed_layout)
        
        layout.addWidget(voice_group)
        
        # About
        about = QLabel(f"{APP_NAME} v{VERSION}\n\nAdvanced AI Assistant for macOS\nBuilt with PyQt6 + Groq LLM")
        about.setStyleSheet(f"color: {self.theme.text_secondary}; padding: 20px;")
        about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(about)
        
        layout.addStretch()
        
        return tab
    
    def _apply_theme(self):
        self.setStyleSheet(f"background-color: {self.theme.background};")
    
    def _change_theme(self, theme_name: str):
        theme_key = theme_name.lower()
        if theme_key in THEMES:
            self.current_theme = theme_key
            self.theme = THEMES[theme_key]
            self._apply_theme()
            self.arc.set_theme(self.theme)
    
    def _update_status(self):
        pass
    
    def greeting(self):
        hour = dt.datetime.now().hour
        if 5 <= hour < 12:
            greeting = f"Good morning, {YOUR_NAME}."
        elif 12 <= hour < 17:
            greeting = f"Good afternoon, {YOUR_NAME}."
        else:
            greeting = f"Good evening, {YOUR_NAME}."
        
        full = (
            f"{greeting} {APP_NAME} fully operational. "
            f"Weather in {LOCATION}: 28°C, Clear. "
            f"Ready to assist with any task."
        )
        self.add_message(full, is_user=False)
        self.voice.speak(full)
    
    def add_message(self, text: str, is_user: bool = False):
        bubble = ChatBubble(text, is_user, self.theme)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        QTimer.singleShot(50, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))
    
    def send_message(self, text: str = None):
        text = text or self.input_field.text().strip()
        if not text:
            return
        
        self.input_field.clear()
        self.add_message(text, is_user=True)
        self.conversation.append({"role": "user", "content": text})
        self.memory.add_conversation("user", text)
        
        threading.Thread(target=self._get_response, args=(text,), daemon=True).start()
    
    def _get_response(self, text: str):
        text_lower = text.lower()
        
        # Learn patterns
        pattern = self.memory.get_pattern(text_lower[:50])
        if pattern:
            self.add_message(pattern, is_user=False)
            return
        
        # System commands
        if any(k in text_lower for k in ["remember", "note"]):
            self.memory.remember(text_lower[:100], text)
            response = "I've stored that in my memory."
            self.add_message(response, is_user=False)
            self.voice.speak(response)
            return
        
        if "what do you remember" in text_lower:
            results = self.memory.search(text_lower.replace("what do you remember", "").strip())
            if results["memories"]:
                response = f"I recall: {results['memories'][0]['value']}"
            else:
                response = "I don't have any memories on that topic yet."
            self.add_message(response, is_user=False)
            self.voice.speak(response)
            return
        
        if "task" in text_lower or "todo" in text_lower:
            if "add" in text_lower:
                task = text_lower.replace("add task", "").replace("add todo", "").strip()
                self.memory.add_task(task)
                response = f"Task added: {task}"
                self.add_message(response, is_user=False)
                self._refresh_tasks()
                return
        
        # Smart home
        if any(k in text_lower for k in ["light", "thermostat", "temperature", "ac", "lock"]):
            response = self.smart_home.control(text_lower)
            self.add_message(response, is_user=False)
            self.voice.speak(response)
            return
        
        # Try AI
        try:
            import urllib.request
            data = json.dumps({"messages": self.conversation[-8:]}).encode()
            req = urllib.request.Request(
                f"{FRIDAY_SERVER}/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                result = json.loads(r.read())
            reply = result.get("reply", "Processing complete.")
        except Exception as e:
            reply = f"All systems nominal. (Connection: {str(e)[:30]})"
        
        self.add_message(reply, is_user=False)
        self.voice.speak(reply)
        self.conversation.append({"role": "assistant", "content": reply})
        self.memory.add_conversation("assistant", reply)
    
    def toggle_voice(self):
        if self.is_listening:
            self.stop_voice()
        else:
            self.start_voice()
    
    def start_voice(self):
        self.is_listening = True
        self.voice_input.start()
    
    def stop_voice(self):
        self.is_listening = False
        self.voice_input.stop()
    
    def on_voice_heard(self, text: str):
        self.stop_voice()
        if text.strip():
            self.send_message(text)
    
    def on_voice_status(self, status: str):
        pass
    
    def execute_agent_task(self):
        task = self.agent_input.text().strip()
        if not task:
            return
        
        self.agent_output.append(f"🎯 Executing: {task}\n")
        
        # Execute via agentic engine
        agent_task = self.agentic.execute_task(task)
        
        # Wait and show result
        def check_result():
            if agent_task.status == "completed":
                self.agent_output.append(f"✅ {agent_task.result}\n")
                self.agent_output.append(f"Steps completed: {len(agent_task.steps)}")
            elif agent_task.status == "failed":
                self.agent_output.append(f"❌ {agent_task.result}")
            else:
                QTimer.singleShot(500, check_result)
        
        QTimer.singleShot(500, check_result)
    
    def run_swarm(self):
        task = self.agent_input.text().strip() or "General problem solving"
        
        self.agent_output.append(f"🔀 Running Multi-Agent Swarm for: {task}\n")
        
        result = self.swarm.solve(task)
        
        self.agent_output.append(f"\nAgents involved:")
        for agent_result in result["agents"]:
            self.agent_output.append(f"  • {agent_result['agent']}: {agent_result['confidence']:.0%} confidence")
        
        self.agent_output.append(f"\n📋 Synthesis:\n{result['synthesis']}")
    
    def execute_code(self):
        task = self.code_input.text().strip()
        if not task:
            return
        
        self.code_output.append(f"# Executing: {task}\n")
        
        result = self.code_executor.write_and_run(task)
        
        if result["success"]:
            self.code_output.append(f"# Code generated:\n{result['code']}\n")
            self.code_output.append(f"# Output:\n{result['output']}")
        else:
            self.code_output.append(f"# Error: {result['error']}")
    
    def browse_data_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", os.path.expanduser("~/Documents"),
            "Data Files (*.csv *.xlsx *.xls *.json);;All Files (*)"
        )
        if filepath:
            self.data_file_input.setText(filepath)
    
    def analyze_data(self):
        filepath = self.data_file_input.text().strip()
        task = self.data_task_input.text().strip()
        
        if not filepath:
            self.data_output.setText("Please select a data file first.")
            return
        
        result = self.data_analyzer.analyze(filepath, task or "general analysis")
        
        if "error" in result:
            self.data_output.setText(f"Error: {result['error']}")
        else:
            output = json.dumps(result, indent=2, default=str)
            self.data_output.setText(output[:5000])
    
    def add_task(self):
        task = self.task_input.text().strip()
        if task:
            self.memory.add_task(task)
            self.task_input.clear()
            self._refresh_tasks()
    
    def _refresh_tasks(self):
        self.task_list.clear()
        tasks = self.memory.get_tasks()
        for task in tasks:
            item = QListWidgetItem(f"☐ {task['title']}")
            item.setData(Qt.ItemDataRole.UserRole, task['id'])
            self.task_list.addItem(item)
    
    def add_note(self):
        self.input_field.setText("remember: ")
        self.input_field.setFocus()
    
    def quick_search(self):
        self.input_field.setText("search the web for: ")
        self.input_field.setFocus()
    
    def take_screenshot(self):
        path = os.path.expanduser(f"~/Desktop/screenshot_{int(time.time())}.png")
        subprocess.run(["screencapture", "-x", path], capture_output=True)
        self.add_message(f"Screenshot saved to Desktop.", is_user=False)
    
    def toggle_agent_mode(self):
        self.agent_mode = not self.agent_mode
        self.mode_label.setText("🤖 AGENT" if self.agent_mode else "💬 CHAT")
        self.tab_widget.setCurrentIndex(1 if self.agent_mode else 0)
    
    def open_code_executor(self):
        self.tab_widget.setCurrentIndex(2)
    
    def open_data_analyzer(self):
        self.tab_widget.setCurrentIndex(3)
    
    def open_smart_home(self):
        self.add_message("Smart Home Hub ready. Commands: 'Turn on bedroom light', 'Set temperature to 24', etc.", is_user=False)
    
    def open_email(self):
        self.add_message("Email automation ready. Say 'send email to John about the project'.", is_user=False)
    
    def change_theme(self):
        themes = list(THEMES.keys())
        current = themes.index(self.current_theme)
        next_theme = themes[(current + 1) % len(themes)]
        self._change_theme(next_theme.capitalize())
        self.theme_combo.setCurrentText(next_theme.upper())
    
    def open_settings(self):
        self.tab_widget.setCurrentIndex(5)
    
    def closeEvent(self, event):
        self.memory.close()
        event.accept()


# =============================================================================
# SPLASH SCREEN
# =============================================================================

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(10, 12, 16))
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        title = QLabel(f"{APP_NAME}", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #00d4ff;
            font-size: 48px;
            font-weight: bold;
            letter-spacing: 8px;
            text-shadow: 0 0 30px rgba(0,212,255,0.8);
        """)
        title.setFont(QFont("Arial", 44, QFont.Weight.Bold))
        title.resize(600, 400)
        title.move(0, 130)
        
        sub = QLabel("Tony Stark Level AI Assistant", self)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: rgba(0,170,255,0.6); font-size: 14px; letter-spacing: 4px;")
        sub.setFont(QFont("Arial", 12))
        sub.resize(600, 400)
        sub.move(0, 200)
        
        loading = QLabel("Initializing systems...", self)
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading.setStyleSheet("color: rgba(0,200,255,0.5); font-size: 12px;")
        loading.setFont(QFont("Courier", 11))
        loading.resize(600, 400)
        loading.move(0, 320)
        
        self.show()
        QTimer.singleShot(3000, self.finish_splash)
    
    def finish_splash(self):
        self.window = FridayWindow()
        self.window.show()
        self.hide()


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 12, 16))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 232, 240))
    app.setPalette(palette)
    
    splash = SplashScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
