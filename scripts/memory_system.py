#!/usr/bin/env python3
"""
Memory System - Persistent storage for AI conversations and project progress
Stores conversation history, ladder discoveries, and insights
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class MemorySystem:
    def __init__(self, db_path='memory.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize memory database with tables"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Conversation history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                action TEXT,
                data TEXT,
                session_id TEXT
            )
        ''')

        # Project progress table (ladder milestones)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS project_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                data TEXT,
                importance INTEGER DEFAULT 5
            )
        ''')

        # Discoveries and insights
        cur.execute('''
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                verified INTEGER DEFAULT 0
            )
        ''')

        # Model learnings (patterns the AI discovers)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                insight TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def save_message(self, role: str, content: str, action: str = None,
                     data: Dict = None, session_id: str = None):
        """Save a conversation message"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO conversations (timestamp, role, content, action, data, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            role,
            content,
            action,
            json.dumps(data) if data else None,
            session_id or 'default'
        ))

        conn.commit()
        conn.close()

    def get_recent_conversations(self, limit: int = 20,
                                 session_id: str = None) -> List[Dict]:
        """Get recent conversation history"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if session_id:
            cur.execute('''
                SELECT timestamp, role, content, action, data
                FROM conversations
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (session_id, limit))
        else:
            cur.execute('''
                SELECT timestamp, role, content, action, data
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))

        rows = cur.fetchall()
        conn.close()

        messages = []
        for row in rows:
            messages.append({
                'timestamp': row[0],
                'role': row[1],
                'content': row[2],
                'action': row[3],
                'data': json.loads(row[4]) if row[4] else None
            })

        return list(reversed(messages))  # Oldest first

    def log_progress(self, event_type: str, description: str,
                     data: Dict = None, importance: int = 5):
        """Log project progress event"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO project_progress (timestamp, event_type, description, data, importance)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event_type,
            description,
            json.dumps(data) if data else None,
            importance
        ))

        conn.commit()
        conn.close()

    def get_progress_summary(self, limit: int = 50) -> List[Dict]:
        """Get recent project progress events"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            SELECT timestamp, event_type, description, data, importance
            FROM project_progress
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))

        rows = cur.fetchall()
        conn.close()

        events = []
        for row in rows:
            events.append({
                'timestamp': row[0],
                'event_type': row[1],
                'description': row[2],
                'data': json.loads(row[3]) if row[3] else None,
                'importance': row[4]
            })

        return list(reversed(events))

    def add_discovery(self, category: str, title: str, content: str,
                     tags: List[str] = None, verified: bool = False):
        """Record a discovery or insight"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO discoveries (timestamp, category, title, content, tags, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            category,
            title,
            content,
            json.dumps(tags) if tags else None,
            1 if verified else 0
        ))

        conn.commit()
        conn.close()

    def get_discoveries(self, category: str = None, verified_only: bool = False) -> List[Dict]:
        """Get discoveries"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if category:
            if verified_only:
                cur.execute('''
                    SELECT timestamp, category, title, content, tags, verified
                    FROM discoveries
                    WHERE category = ? AND verified = 1
                    ORDER BY id DESC
                ''', (category,))
            else:
                cur.execute('''
                    SELECT timestamp, category, title, content, tags, verified
                    FROM discoveries
                    WHERE category = ?
                    ORDER BY id DESC
                ''', (category,))
        else:
            if verified_only:
                cur.execute('''
                    SELECT timestamp, category, title, content, tags, verified
                    FROM discoveries
                    WHERE verified = 1
                    ORDER BY id DESC
                ''')
            else:
                cur.execute('''
                    SELECT timestamp, category, title, content, tags, verified
                    FROM discoveries
                    ORDER BY id DESC
                ''')

        rows = cur.fetchall()
        conn.close()

        discoveries = []
        for row in rows:
            discoveries.append({
                'timestamp': row[0],
                'category': row[1],
                'title': row[2],
                'content': row[3],
                'tags': json.loads(row[4]) if row[4] else [],
                'verified': bool(row[5])
            })

        return discoveries

    def add_learning(self, topic: str, insight: str, confidence: float = 0.5,
                    source: str = None):
        """Record an AI learning/insight"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO learnings (timestamp, topic, insight, confidence, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            topic,
            insight,
            confidence,
            source
        ))

        conn.commit()
        conn.close()

    def get_learnings(self, topic: str = None, min_confidence: float = 0.0) -> List[Dict]:
        """Get AI learnings"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if topic:
            cur.execute('''
                SELECT timestamp, topic, insight, confidence, source
                FROM learnings
                WHERE topic = ? AND confidence >= ?
                ORDER BY confidence DESC, id DESC
            ''', (topic, min_confidence))
        else:
            cur.execute('''
                SELECT timestamp, topic, insight, confidence, source
                FROM learnings
                WHERE confidence >= ?
                ORDER BY confidence DESC, id DESC
            ''', (min_confidence,))

        rows = cur.fetchall()
        conn.close()

        learnings = []
        for row in rows:
            learnings.append({
                'timestamp': row[0],
                'topic': row[1],
                'insight': row[2],
                'confidence': row[3],
                'source': row[4]
            })

        return learnings

    def build_context_summary(self) -> str:
        """Build a context summary for the AI model"""
        # Get recent progress
        progress = self.get_progress_summary(limit=10)

        # Get verified discoveries
        discoveries = self.get_discoveries(verified_only=True)

        # Get high-confidence learnings
        learnings = self.get_learnings(min_confidence=0.7)

        context = "# PROJECT MEMORY AND CONTEXT\n\n"

        if progress:
            context += "## Recent Progress:\n"
            for event in progress[-5:]:  # Last 5 events
                context += f"- [{event['event_type']}] {event['description']}\n"
            context += "\n"

        if discoveries:
            context += "## Verified Discoveries:\n"
            for disc in discoveries[:5]:  # Top 5 discoveries
                context += f"- **{disc['title']}**: {disc['content']}\n"
            context += "\n"

        if learnings:
            context += "## Key Learnings:\n"
            for learn in learnings[:5]:  # Top 5 learnings
                context += f"- [{learn['topic']}] {learn['insight']} (confidence: {learn['confidence']:.0%})\n"
            context += "\n"

        return context

    def get_conversation_context(self, limit: int = 10) -> str:
        """Get recent conversation context formatted for the model"""
        messages = self.get_recent_conversations(limit=limit)

        if not messages:
            return ""

        context = "## Recent Conversation:\n"
        for msg in messages:
            role_name = "User" if msg['role'] == 'user' else "Assistant"
            context += f"**{role_name}**: {msg['content'][:200]}...\n" if len(msg['content']) > 200 else f"**{role_name}**: {msg['content']}\n"

        return context

# Global memory instance
_memory_system = None

# Use absolute path for the database
import os
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'memory.db')

def get_memory_system(db_path=None) -> MemorySystem:
    """Get or create global memory system"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem(db_path or _DEFAULT_DB_PATH)
    return _memory_system

if __name__ == '__main__':
    # Test the memory system
    print("🧠 Testing Memory System")
    print("=" * 60)

    memory = MemorySystem('test_memory.db')

    # Test conversation storage
    print("\n📝 Testing conversation storage...")
    memory.save_message('user', 'Hello, test message')
    memory.save_message('assistant', 'Hello! How can I help?')

    messages = memory.get_recent_conversations(limit=10)
    print(f"✓ Stored {len(messages)} messages")

    # Test progress logging
    print("\n📊 Testing progress logging...")
    memory.log_progress('verification', 'Achieved 100% verification', importance=10)
    memory.log_progress('generation', 'Generated puzzle 71', importance=9)

    progress = memory.get_progress_summary()
    print(f"✓ Logged {len(progress)} progress events")

    # Test discoveries
    print("\n🔍 Testing discoveries...")
    memory.add_discovery(
        'byte_order',
        'Little-endian in database',
        'Database uses little-endian byte order, CSV uses big-endian',
        tags=['critical', 'byte-order'],
        verified=True
    )

    discoveries = memory.get_discoveries()
    print(f"✓ Recorded {len(discoveries)} discoveries")

    # Test learnings
    print("\n🎓 Testing learnings...")
    memory.add_learning(
        'affine_recurrence',
        'The ladder follows y = A×x + C mod 256 with 16 parallel lanes',
        confidence=0.95,
        source='verified_analysis'
    )

    learnings = memory.get_learnings()
    print(f"✓ Recorded {len(learnings)} learnings")

    # Build context
    print("\n🧠 Building context summary...")
    context = memory.build_context_summary()
    print(context)

    print("\n✅ All tests passed!")

    # Cleanup
    import os
    os.remove('test_memory.db')
