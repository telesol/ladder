#!/usr/bin/env python3
"""
Orchestrator - Central coordinator for the Ladder Agents system
Uses Ollama Cloud API for task planning and result synthesis
"""
import os
import json
import asyncio
import sqlite3
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml

from .math_agent import MathAgent
from .verification_agent import VerificationAgent
from .discovery_agent import DiscoveryAgent

class ClaudeOrchestrator:
    """Central orchestrator using Ollama for planning and synthesis"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Initialize Ollama client settings
        orch_config = self.config['orchestrator']
        self.base_url = orch_config.get('base_url', 'https://api.ollama.com')
        self.model = orch_config.get('model', 'qwen2.5:72b')
        self.max_tokens = orch_config.get('max_tokens', 4096)
        self.temperature = orch_config.get('temperature', 0.7)
        self.api_key = os.getenv(orch_config.get('api_key_env', 'OLLAMA_API_KEY'))

        # Initialize agents
        self.math_agent = MathAgent()
        self.verification_agent = VerificationAgent()
        self.discovery_agent = DiscoveryAgent()

        # Memory database
        self.memory_db = os.path.join(self.base_dir, self.config['databases']['memory_db'])
        self._init_memory_db()

        # Task queue
        self.task_queue: List[Dict] = []
        self.results: List[Dict] = []

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, config_path)
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _init_memory_db(self):
        """Initialize memory database"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()

        # Tasks table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                task_type TEXT NOT NULL,
                agent TEXT NOT NULL,
                input TEXT,
                output TEXT,
                status TEXT DEFAULT 'pending',
                duration_ms INTEGER
            )
        ''')

        # Discoveries table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                verified INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    async def call_claude(self, prompt: str, system: str = None) -> str:
        """Call Ollama API for orchestration decisions"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": self._get_system_prompt()})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        # Handle both JSON and text/plain responses
                        text_response = await response.text()
                        try:
                            result = json.loads(text_response)
                            return result.get('message', {}).get('content', '')
                        except json.JSONDecodeError:
                            return text_response
                    else:
                        error = await response.text()
                        return f"Ollama API error: {response.status} - {error}"
        except Exception as e:
            return f"Ollama API error: {str(e)}"

    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude orchestrator"""
        return """You are the orchestrator for the Ladder Agents system, a 24/7 autonomous Bitcoin puzzle discovery project.

Your agents:
1. MathAgent - Handles affine recurrence calculations, drift computation
2. VerificationAgent - Cryptographic validation, address generation
3. DiscoveryAgent - Pattern discovery, hypothesis generation

Your role:
- Plan and decompose complex tasks
- Dispatch work to appropriate agents
- Synthesize results into actionable insights
- Track progress and discoveries
- Ensure mathematical rigor (NO STUBS, NO HARDCODING)

The mathematical model:
- y = A[l] * x + C[k][l][occ] (mod 256)
- 16 parallel lanes
- Goal: Reconstruct the complete ladder and solve puzzle 71+

Always output structured JSON for task dispatches."""

    async def plan_task(self, goal: str) -> List[Dict]:
        """Use Claude to plan how to achieve a goal"""
        prompt = f"""Given this goal: {goal}

Break it down into specific tasks for the agents.
Each task should be a JSON object with:
- agent: "math", "verification", or "discovery"
- type: specific task type for that agent
- params: any parameters needed

Output a JSON array of tasks in execution order.
Consider dependencies between tasks.

Available task types:
- math: compute_drift, verify, forward_step, analyze
- verification: validate, verify_against_known, full_verify
- discovery: analyze_lane, find_anomalies, hypothesis, explore

Return ONLY valid JSON."""

        response = await self.call_claude(prompt)

        # Parse JSON from response
        try:
            # Find JSON in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                tasks = json.loads(response[start:end])
                return tasks
        except json.JSONDecodeError:
            pass

        # Fallback: simple task
        return [{"agent": "discovery", "type": "explore", "params": {}}]

    async def dispatch_task(self, task: Dict) -> Dict:
        """Dispatch a task to the appropriate agent"""
        agent_name = task.get("agent", "discovery")
        task_type = task.get("type", "explore")
        params = task.get("params", {})

        start_time = datetime.now()

        # Build task dict for agent
        agent_task = {"type": task_type, **params}

        # Dispatch to agent
        if agent_name == "math":
            result = await self.math_agent.execute(agent_task)
        elif agent_name == "verification":
            result = await self.verification_agent.execute(agent_task)
        elif agent_name == "discovery":
            result = await self.discovery_agent.execute(agent_task)
        else:
            result = {"error": f"Unknown agent: {agent_name}"}

        duration = (datetime.now() - start_time).total_seconds() * 1000

        # Log to database
        self._log_task(task_type, agent_name, params, result, duration)

        return {
            "task": task,
            "result": result,
            "duration_ms": duration
        }

    def _log_task(self, task_type: str, agent: str, input_data: Dict,
                  output_data: Dict, duration: float):
        """Log task to database"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO tasks (timestamp, task_type, agent, input, output, status, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            task_type,
            agent,
            json.dumps(input_data),
            json.dumps(output_data),
            'completed',
            int(duration)
        ))
        conn.commit()
        conn.close()

    def save_discovery(self, agent: str, category: str, title: str,
                       content: str, confidence: float = 0.5, verified: bool = False):
        """Save a discovery to database"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO discoveries (timestamp, agent, category, title, content, confidence, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            agent,
            category,
            title,
            content,
            confidence,
            1 if verified else 0
        ))
        conn.commit()
        conn.close()

    async def execute_goal(self, goal: str) -> Dict:
        """Execute a complete goal from planning to synthesis"""
        self.log(f"Starting goal: {goal}")

        # Plan tasks
        tasks = await self.plan_task(goal)
        self.log(f"Planned {len(tasks)} tasks")

        # Execute tasks
        results = []
        for i, task in enumerate(tasks):
            self.log(f"Executing task {i+1}/{len(tasks)}: {task.get('type')}")
            result = await self.dispatch_task(task)
            results.append(result)

            # Check for discoveries in result
            if isinstance(result.get('result'), dict):
                if result['result'].get('type') == 'discovery':
                    self.save_discovery(
                        agent=task.get('agent'),
                        category=result['result'].get('category', 'general'),
                        title=result['result'].get('title', 'Untitled'),
                        content=json.dumps(result['result']),
                        confidence=result['result'].get('confidence', 0.5)
                    )

        # Synthesize results
        synthesis = await self.synthesize_results(goal, results)

        return {
            "goal": goal,
            "tasks": len(tasks),
            "results": results,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat()
        }

    async def synthesize_results(self, goal: str, results: List[Dict]) -> str:
        """Use Claude to synthesize results into insights"""
        prompt = f"""Goal: {goal}

Results from agents:
{json.dumps(results, indent=2, default=str)[:4000]}

Synthesize these results into:
1. Key findings
2. Progress toward the goal
3. Next steps
4. Any discoveries worth saving

Be concise and actionable."""

        return await self.call_claude(prompt)

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [Orchestrator] [{level}] {message}")

    async def run_discovery_cycle(self):
        """Run one discovery cycle (for daemon mode)"""
        # Autonomous discovery task
        goal = "Explore the ladder patterns and find new insights"
        return await self.execute_goal(goal)

    def get_recent_tasks(self, limit: int = 20) -> List[Dict]:
        """Get recent tasks from database"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()
        cur.execute('''
            SELECT timestamp, task_type, agent, output, duration_ms
            FROM tasks
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "timestamp": r[0],
                "task_type": r[1],
                "agent": r[2],
                "output": json.loads(r[3]) if r[3] else None,
                "duration_ms": r[4]
            }
            for r in rows
        ]

    def get_discoveries(self, verified_only: bool = False) -> List[Dict]:
        """Get discoveries from database"""
        conn = sqlite3.connect(self.memory_db)
        cur = conn.cursor()
        if verified_only:
            cur.execute('SELECT * FROM discoveries WHERE verified = 1 ORDER BY id DESC')
        else:
            cur.execute('SELECT * FROM discoveries ORDER BY id DESC')
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "agent": r[2],
                "category": r[3],
                "title": r[4],
                "content": r[5],
                "confidence": r[6],
                "verified": bool(r[7])
            }
            for r in rows
        ]


# Standalone execution
if __name__ == "__main__":
    async def main():
        orchestrator = ClaudeOrchestrator()
        print("Claude Orchestrator initialized")

        # Test with a simple goal
        result = await orchestrator.execute_goal("Analyze lane 0 patterns and find anomalies")
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(main())
