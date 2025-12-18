#!/usr/bin/env python3
"""
Agent Memory System - Persistent memory for multi-agent architecture
Extends the base memory system with per-agent context and shared knowledge.

Features:
- Per-agent conversation history
- Shared discoveries across agents
- Agent-specific insights and learnings
- Cross-agent communication log
- Oracle query history with full responses
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_memory.db')


class AgentMemory:
    """Memory system for the multi-agent architecture"""

    AGENTS = ['a-solver', 'b-solver', 'c-solver', 'maestro']

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.init_database()

    def init_database(self):
        """Initialize agent memory database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Agent sessions - track agent activity
        cur.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'active',
                summary TEXT
            )
        ''')

        # Agent conversations - per-agent query history
        cur.execute('''
            CREATE TABLE IF NOT EXISTS agent_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tokens_used INTEGER,
                response_time REAL,
                session_id INTEGER,
                FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
            )
        ''')

        # Agent insights - what each agent has discovered
        cur.execute('''
            CREATE TABLE IF NOT EXISTS agent_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                insight TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                verified INTEGER DEFAULT 0,
                source_query TEXT,
                tags TEXT
            )
        ''')

        # Shared knowledge - cross-agent verified facts
        cur.execute('''
            CREATE TABLE IF NOT EXISTS shared_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                fact_type TEXT NOT NULL,
                fact TEXT NOT NULL,
                discovered_by TEXT NOT NULL,
                verified_by TEXT,
                confidence REAL DEFAULT 0.5,
                metadata TEXT
            )
        ''')

        # Oracle queries - full oracle query/response log
        cur.execute('''
            CREATE TABLE IF NOT EXISTS oracle_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT,
                response_length INTEGER,
                response_time REAL,
                model TEXT,
                extracted_insights TEXT
            )
        ''')

        # Agent status - current state of each agent
        cur.execute('''
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_id TEXT PRIMARY KEY,
                last_active TEXT,
                total_queries INTEGER DEFAULT 0,
                total_insights INTEGER DEFAULT 0,
                certification_status TEXT,
                certification_score TEXT,
                model TEXT,
                specialty TEXT
            )
        ''')

        # Initialize agent status if not exists
        for agent in self.AGENTS:
            cur.execute('''
                INSERT OR IGNORE INTO agent_status (agent_id, last_active)
                VALUES (?, ?)
            ''', (agent, datetime.now().isoformat()))

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_agent_conv_agent ON agent_conversations(agent_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_agent_conv_time ON agent_conversations(timestamp)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_oracle_time ON oracle_queries(timestamp)')

        conn.commit()
        conn.close()

    # ============ Agent Conversations ============

    def save_agent_message(self, agent_id: str, role: str, content: str,
                           tokens: int = None, response_time: float = None):
        """Save an agent conversation message"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO agent_conversations (agent_id, timestamp, role, content, tokens_used, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_id, datetime.now().isoformat(), role, content, tokens, response_time))

        # Update agent status
        cur.execute('''
            UPDATE agent_status
            SET last_active = ?, total_queries = total_queries + 1
            WHERE agent_id = ?
        ''', (datetime.now().isoformat(), agent_id))

        conn.commit()
        conn.close()

    def get_agent_history(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """Get recent conversation history for an agent"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            SELECT timestamp, role, content, tokens_used, response_time
            FROM agent_conversations
            WHERE agent_id = ?
            ORDER BY id DESC
            LIMIT ?
        ''', (agent_id, limit))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[0],
                'role': row[1],
                'content': row[2],
                'tokens': row[3],
                'response_time': row[4]
            }
            for row in reversed(rows)
        ]

    def get_all_agent_history(self, limit: int = 50) -> Dict[str, List[Dict]]:
        """Get recent history for all agents"""
        return {
            agent: self.get_agent_history(agent, limit // 4)
            for agent in self.AGENTS
        }

    # ============ Oracle Queries ============

    def save_oracle_query(self, agent_id: str, query: str, response: str,
                          response_time: float = None, model: str = None,
                          insights: List[str] = None):
        """Save an oracle query and response"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO oracle_queries
            (timestamp, agent_id, query, response, response_length, response_time, model, extracted_insights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            agent_id,
            query,
            response,
            len(response) if response else 0,
            response_time,
            model,
            json.dumps(insights) if insights else None
        ))

        conn.commit()
        conn.close()

    def get_oracle_history(self, agent_id: str = None, limit: int = 20) -> List[Dict]:
        """Get oracle query history"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if agent_id:
            cur.execute('''
                SELECT timestamp, agent_id, query, response, response_length, response_time, model
                FROM oracle_queries
                WHERE agent_id = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (agent_id, limit))
        else:
            cur.execute('''
                SELECT timestamp, agent_id, query, response, response_length, response_time, model
                FROM oracle_queries
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))

        rows = cur.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[0],
                'agent_id': row[1],
                'query': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                'response_preview': row[3][:500] + '...' if row[3] and len(row[3]) > 500 else row[3],
                'response_length': row[4],
                'response_time': row[5],
                'model': row[6]
            }
            for row in rows
        ]

    # ============ Agent Insights ============

    def add_agent_insight(self, agent_id: str, category: str, insight: str,
                          confidence: float = 0.5, source_query: str = None,
                          tags: List[str] = None):
        """Record an insight from an agent"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO agent_insights
            (agent_id, timestamp, category, insight, confidence, source_query, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id,
            datetime.now().isoformat(),
            category,
            insight,
            confidence,
            source_query,
            json.dumps(tags) if tags else None
        ))

        # Update agent insight count
        cur.execute('''
            UPDATE agent_status
            SET total_insights = total_insights + 1
            WHERE agent_id = ?
        ''', (agent_id,))

        conn.commit()
        conn.close()

    def get_agent_insights(self, agent_id: str = None, category: str = None,
                           min_confidence: float = 0.0) -> List[Dict]:
        """Get insights from agents"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = '''
            SELECT agent_id, timestamp, category, insight, confidence, verified, tags
            FROM agent_insights
            WHERE confidence >= ?
        '''
        params = [min_confidence]

        if agent_id:
            query += ' AND agent_id = ?'
            params.append(agent_id)
        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY confidence DESC, id DESC LIMIT 100'

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        return [
            {
                'agent_id': row[0],
                'timestamp': row[1],
                'category': row[2],
                'insight': row[3],
                'confidence': row[4],
                'verified': bool(row[5]),
                'tags': json.loads(row[6]) if row[6] else []
            }
            for row in rows
        ]

    def verify_insight(self, insight_id: int, verifying_agent: str = 'maestro'):
        """Mark an insight as verified"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            UPDATE agent_insights
            SET verified = 1
            WHERE id = ?
        ''', (insight_id,))

        conn.commit()
        conn.close()

    # ============ Shared Knowledge ============

    def add_shared_knowledge(self, fact_type: str, fact: str, discovered_by: str,
                             confidence: float = 0.5, metadata: Dict = None):
        """Add a fact to shared knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO shared_knowledge
            (timestamp, fact_type, fact, discovered_by, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            fact_type,
            fact,
            discovered_by,
            confidence,
            json.dumps(metadata) if metadata else None
        ))

        conn.commit()
        conn.close()

    def get_shared_knowledge(self, fact_type: str = None) -> List[Dict]:
        """Get shared knowledge facts"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if fact_type:
            cur.execute('''
                SELECT timestamp, fact_type, fact, discovered_by, verified_by, confidence
                FROM shared_knowledge
                WHERE fact_type = ?
                ORDER BY confidence DESC
            ''', (fact_type,))
        else:
            cur.execute('''
                SELECT timestamp, fact_type, fact, discovered_by, verified_by, confidence
                FROM shared_knowledge
                ORDER BY confidence DESC
            ''')

        rows = cur.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[0],
                'fact_type': row[1],
                'fact': row[2],
                'discovered_by': row[3],
                'verified_by': row[4],
                'confidence': row[5]
            }
            for row in rows
        ]

    # ============ Agent Status ============

    def update_agent_status(self, agent_id: str, certification_status: str = None,
                            certification_score: str = None, model: str = None,
                            specialty: str = None):
        """Update agent status"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        updates = ['last_active = ?']
        params = [datetime.now().isoformat()]

        if certification_status:
            updates.append('certification_status = ?')
            params.append(certification_status)
        if certification_score:
            updates.append('certification_score = ?')
            params.append(certification_score)
        if model:
            updates.append('model = ?')
            params.append(model)
        if specialty:
            updates.append('specialty = ?')
            params.append(specialty)

        params.append(agent_id)

        cur.execute(f'''
            UPDATE agent_status
            SET {', '.join(updates)}
            WHERE agent_id = ?
        ''', params)

        conn.commit()
        conn.close()

    def get_agent_status(self, agent_id: str = None) -> Dict:
        """Get agent status"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        if agent_id:
            cur.execute('''
                SELECT agent_id, last_active, total_queries, total_insights,
                       certification_status, certification_score, model, specialty
                FROM agent_status
                WHERE agent_id = ?
            ''', (agent_id,))
            row = cur.fetchone()
            conn.close()

            if row:
                return {
                    'agent_id': row[0],
                    'last_active': row[1],
                    'total_queries': row[2],
                    'total_insights': row[3],
                    'certification_status': row[4],
                    'certification_score': row[5],
                    'model': row[6],
                    'specialty': row[7]
                }
            return None
        else:
            cur.execute('''
                SELECT agent_id, last_active, total_queries, total_insights,
                       certification_status, certification_score, model, specialty
                FROM agent_status
            ''')
            rows = cur.fetchall()
            conn.close()

            return {
                row[0]: {
                    'agent_id': row[0],
                    'last_active': row[1],
                    'total_queries': row[2],
                    'total_insights': row[3],
                    'certification_status': row[4],
                    'certification_score': row[5],
                    'model': row[6],
                    'specialty': row[7]
                }
                for row in rows
            }

    # ============ Context Building ============

    def build_agent_context(self, agent_id: str, include_shared: bool = True) -> str:
        """Build context for an agent including its history and shared knowledge"""
        context = f"# {agent_id.upper()} MEMORY CONTEXT\n\n"

        # Recent conversations
        history = self.get_agent_history(agent_id, limit=5)
        if history:
            context += "## Recent Queries:\n"
            for msg in history[-3:]:
                if msg['role'] == 'user':
                    context += f"- Q: {msg['content'][:100]}...\n"
            context += "\n"

        # Agent insights
        insights = self.get_agent_insights(agent_id=agent_id, min_confidence=0.6)
        if insights:
            context += "## Your Key Insights:\n"
            for ins in insights[:5]:
                context += f"- [{ins['category']}] {ins['insight'][:100]} (conf: {ins['confidence']:.0%})\n"
            context += "\n"

        # Shared knowledge
        if include_shared:
            shared = self.get_shared_knowledge()
            if shared:
                context += "## Shared Knowledge:\n"
                for fact in shared[:5]:
                    context += f"- [{fact['fact_type']}] {fact['fact'][:100]}\n"
                context += "\n"

        return context

    def get_statistics(self) -> Dict:
        """Get overall memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        stats = {}

        # Total conversations
        cur.execute('SELECT COUNT(*) FROM agent_conversations')
        stats['total_conversations'] = cur.fetchone()[0]

        # Total oracle queries
        cur.execute('SELECT COUNT(*) FROM oracle_queries')
        stats['total_oracle_queries'] = cur.fetchone()[0]

        # Total insights
        cur.execute('SELECT COUNT(*) FROM agent_insights')
        stats['total_insights'] = cur.fetchone()[0]

        # Verified insights
        cur.execute('SELECT COUNT(*) FROM agent_insights WHERE verified = 1')
        stats['verified_insights'] = cur.fetchone()[0]

        # Shared knowledge
        cur.execute('SELECT COUNT(*) FROM shared_knowledge')
        stats['shared_knowledge_count'] = cur.fetchone()[0]

        # Per-agent stats
        cur.execute('''
            SELECT agent_id, COUNT(*) as queries
            FROM agent_conversations
            GROUP BY agent_id
        ''')
        stats['per_agent_queries'] = {row[0]: row[1] for row in cur.fetchall()}

        conn.close()
        return stats


    # ============ Conversation Compaction ============

    def compact_conversation(self, agent_id: str, max_tokens: int = 8000,
                            keep_recent: int = 5) -> str:
        """
        Compact conversation history to stay within token limits.
        Returns a summary of older messages while keeping recent ones intact.

        Args:
            agent_id: The agent whose conversation to compact
            max_tokens: Approximate max tokens to keep (1 token ≈ 4 chars)
            keep_recent: Number of recent messages to keep uncompacted

        Returns:
            Compacted context string
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get all messages for this agent
        cur.execute('''
            SELECT id, timestamp, role, content, tokens_used
            FROM agent_conversations
            WHERE agent_id = ?
            ORDER BY id ASC
        ''', (agent_id,))

        all_messages = cur.fetchall()

        if len(all_messages) <= keep_recent:
            conn.close()
            return self.build_agent_context(agent_id)

        # Split into old (to summarize) and recent (to keep)
        old_messages = all_messages[:-keep_recent]
        recent_messages = all_messages[-keep_recent:]

        # Estimate total chars (4 chars ≈ 1 token)
        total_chars = sum(len(m[3]) for m in all_messages)
        max_chars = max_tokens * 4

        if total_chars <= max_chars:
            conn.close()
            return self.build_agent_context(agent_id)

        # Create summary of old messages
        summary_parts = []
        for msg in old_messages:
            timestamp, role, content = msg[1], msg[2], msg[3]
            # Truncate each old message to key points
            if len(content) > 200:
                summary_parts.append(f"[{role}] {content[:200]}...")
            else:
                summary_parts.append(f"[{role}] {content}")

        # Save compaction record
        summary = "COMPACTED HISTORY:\n" + "\n".join(summary_parts[-10:])  # Keep last 10 summaries

        cur.execute('''
            INSERT INTO agent_conversations
            (agent_id, timestamp, role, content, tokens_used)
            VALUES (?, ?, 'system', ?, ?)
        ''', (agent_id, datetime.now().isoformat(),
              f"[COMPACTION] {len(old_messages)} messages summarized",
              len(summary) // 4))

        # Delete old messages that were compacted
        old_ids = [m[0] for m in old_messages[:-5]]  # Keep some buffer
        if old_ids:
            cur.execute(f'''
                DELETE FROM agent_conversations
                WHERE id IN ({','.join('?' * len(old_ids))})
            ''', old_ids)

        conn.commit()
        conn.close()

        return summary + "\n\nRECENT CONTEXT:\n" + self.build_agent_context(agent_id)

    def get_compacted_context(self, agent_id: str, max_tokens: int = 4000) -> str:
        """
        Get context for an agent, automatically compacting if needed.
        Suitable for feeding to models with limited context windows.
        """
        # Get current context
        context = self.build_agent_context(agent_id)

        # Check if compaction needed (rough estimate: 4 chars = 1 token)
        estimated_tokens = len(context) // 4

        if estimated_tokens > max_tokens:
            context = self.compact_conversation(agent_id, max_tokens)

        return context

    def save_full_oracle_output(self, agent_id: str, task: str, prompt: str,
                                response: str, elapsed: float, model: str,
                                compress: bool = True) -> int:
        """
        Save a complete oracle output with optional compression for large responses.

        Returns: The oracle query ID
        """
        import zlib
        import base64

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Compress if response is large and compression requested
        response_to_store = response
        is_compressed = 0

        if compress and len(response) > 50000:
            compressed = zlib.compress(response.encode('utf-8'))
            response_to_store = base64.b64encode(compressed).decode('ascii')
            is_compressed = 1

        cur.execute('''
            INSERT INTO oracle_queries
            (timestamp, agent_id, query, response, response_length, response_time, model, extracted_insights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            agent_id,
            f"[{task}] {prompt[:500]}",
            response_to_store,
            len(response),
            elapsed,
            model,
            json.dumps({'task': task, 'compressed': is_compressed})
        ))

        query_id = cur.lastrowid
        conn.commit()
        conn.close()

        return query_id

    def get_full_oracle_response(self, query_id: int) -> Optional[str]:
        """
        Retrieve a full oracle response, decompressing if needed.
        """
        import zlib
        import base64

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            SELECT response, extracted_insights
            FROM oracle_queries
            WHERE id = ?
        ''', (query_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        response, insights_json = row

        # Check if compressed
        try:
            insights = json.loads(insights_json) if insights_json else {}
            if insights.get('compressed'):
                compressed = base64.b64decode(response.encode('ascii'))
                return zlib.decompress(compressed).decode('utf-8')
        except:
            pass

        return response

    def get_db_size(self) -> dict:
        """Get database size information"""
        import os

        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Table sizes (row counts)
        tables = {}
        for table in ['agent_conversations', 'oracle_queries', 'agent_insights', 'shared_knowledge']:
            cur.execute(f'SELECT COUNT(*) FROM {table}')
            tables[table] = cur.fetchone()[0]

        conn.close()

        return {
            'total_size_mb': db_size / (1024 * 1024),
            'tables': tables
        }

    def vacuum_database(self):
        """Compact the SQLite database file"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('VACUUM')
        conn.close()


# Global instance
_agent_memory = None


def get_agent_memory(db_path: str = None) -> AgentMemory:
    """Get or create global agent memory"""
    global _agent_memory
    if _agent_memory is None:
        _agent_memory = AgentMemory(db_path)
    return _agent_memory


# Initialize with default agent info
def initialize_agents():
    """Initialize agents with their default configuration"""
    memory = get_agent_memory()

    agents_config = {
        'a-solver': {
            'model': 'qwen3-vl:8b',
            'specialty': 'Fast analysis, wallet forensics',
            'certification_status': 'certified',
            'certification_score': '10/10'
        },
        'b-solver': {
            'model': 'phi4-reasoning:14b',
            'specialty': 'Deep reasoning, anomaly detection',
            'certification_status': 'training',
            'certification_score': '7/12'
        },
        'c-solver': {
            'model': 'qwq:32b',
            'specialty': 'Prediction, synthesis, mathematical reasoning',
            'certification_status': 'oracle',
            'certification_score': 'Oracle mode'
        },
        'maestro': {
            'model': 'Claude (Opus)',
            'specialty': 'Orchestration, coordination',
            'certification_status': 'active',
            'certification_score': 'N/A'
        }
    }

    for agent_id, config in agents_config.items():
        memory.update_agent_status(agent_id, **config)


if __name__ == '__main__':
    print("Agent Memory System - Testing")
    print("=" * 60)

    memory = AgentMemory('test_agent_memory.db')

    # Initialize agents
    print("\nInitializing agents...")
    for agent in memory.AGENTS:
        memory.update_agent_status(agent, model='test', specialty='testing')

    # Test conversation
    print("\nTesting conversation storage...")
    memory.save_agent_message('a-solver', 'user', 'Analyze k69 position')
    memory.save_agent_message('a-solver', 'assistant', 'k69 is at 0.72% position')

    history = memory.get_agent_history('a-solver')
    print(f"  Stored {len(history)} messages")

    # Test oracle query
    print("\nTesting oracle query storage...")
    memory.save_oracle_query(
        'c-solver',
        'What is the underlying pattern?',
        'Based on analysis, the pattern shows...',
        response_time=45.2,
        model='qwq:32b'
    )

    oracle_history = memory.get_oracle_history()
    print(f"  Stored {len(oracle_history)} oracle queries")

    # Test insights
    print("\nTesting insight storage...")
    memory.add_agent_insight(
        'b-solver',
        'position_pattern',
        'Keys at extreme positions suggest deliberate placement',
        confidence=0.85,
        tags=['position', 'anomaly']
    )

    insights = memory.get_agent_insights()
    print(f"  Stored {len(insights)} insights")

    # Test shared knowledge
    print("\nTesting shared knowledge...")
    memory.add_shared_knowledge(
        'verified_pattern',
        'k5 = k2 x k3 = 3 x 7 = 21',
        'a-solver',
        confidence=1.0
    )

    shared = memory.get_shared_knowledge()
    print(f"  Stored {len(shared)} shared facts")

    # Test context building
    print("\nBuilding agent context...")
    context = memory.build_agent_context('a-solver')
    print(f"  Context length: {len(context)} chars")

    # Statistics
    print("\nStatistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nAll tests passed!")

    # Cleanup
    os.remove('test_agent_memory.db')
