#!/usr/bin/env python3
"""
Agent Orchestrator V2 - Model-First Architecture

The AI model IS the system. All reasoning goes through the trained model.
No hardcoded responses. No subprocess calls for math. Pure AI reasoning.
"""
import json
from log_integration import get_system_logger, get_ai_logger, get_memory_logger
import os
from datetime import datetime
from typing import Dict, Optional, List

from ollama_integration import list_ollama_models_sync, generate_with_ollama_sync, chat_with_ollama_sync
from context_builder import (
    build_full_context,
    build_drift_computation_context,
    build_calibration_context,
    build_data_context,
    load_calibration,
    get_puzzle_values
)
from model_prompts import get_system_prompt, LADDER_SYSTEM_PROMPT
from memory_system import get_memory_system


class LadderAgent:
    """
    The Ladder AI Agent - routes everything through the trained model.

    This agent:
    1. Receives user messages
    2. Builds appropriate context (calibration, puzzle data)
    3. Sends to the trained model with proper system prompt
    4. Returns the model's mathematical reasoning
    """

    def __init__(self):
        self.memory = get_memory_system()
        self.model_name = "mistral-large-3:675b-cloud"  # Default to available model
        self.conversation_history = []
        self._rag_context = ""  # RAG context from memory/database

        # Load conversation history from persistent storage
        self.conversation_history = self.memory.get_recent_conversations(limit=20)

    def process_message(self, user_message: str) -> Dict:
        """Process a user message through the AI model

        Args:
            user_message: The user's input

        Returns:
            Dict with 'message', optional 'data', and 'action_taken'
        """
        # Save user message
        self.memory.save_message('user', user_message)
        self.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })

        # Determine the task type and build appropriate context
        task_type = self._classify_task(user_message)
        context = self._build_context_for_task(task_type, user_message)
        system_prompt = get_system_prompt(task_type)

        # Build the full prompt with conversation history and RAG context
        conversation_context = self._build_conversation_context()
        rag_section = f"\n{self._rag_context}\n" if self._rag_context else ""
        full_prompt = f"{context}\n{rag_section}\n{conversation_context}\n\nUser: {user_message}"

        # Get model response using Ollama
        response = generate_with_ollama_sync(
            model=self.model_name,
            prompt=full_prompt,
            system=system_prompt,
            max_tokens=4096,
            temperature=0.1  # Low temperature for mathematical reasoning
        )

        if response is None or response.startswith("Error"):
            response = "I encountered an error generating a response. Please try again."

        # Save assistant response
        self.memory.save_message(
            'assistant',
            response,
            action=task_type,
            data={'model_generated': True}
        )

        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'action': task_type
        })

        return {
            'message': response,
            'action_taken': task_type,
            'data': {'model_generated': True}
        }

    def _classify_task(self, message: str) -> str:
        """Classify what type of task the user is asking for

        Unlike V1, we don't use regex pattern matching.
        We let the model understand naturally, but we still
        select appropriate context based on keywords.
        """
        message_lower = message.lower()

        # Drift computation
        if any(word in message_lower for word in ['drift', 'c_0', 'c0', 'compute c']):
            return 'drift'

        # Verification
        if any(word in message_lower for word in ['verify', 'verification', 'check', 'test']):
            return 'verify'

        # Generation
        if any(word in message_lower for word in ['generate', 'puzzle', 'next puzzle', 'predict']):
            return 'generate'

        # General mathematical reasoning
        return 'general'

    def _build_context_for_task(self, task_type: str, message: str) -> str:
        """Build the appropriate context for the task type"""

        if task_type == 'drift':
            # Include specific lane if mentioned
            lane = self._extract_lane_number(message)
            return build_drift_computation_context(lane=lane)

        elif task_type == 'verify':
            return build_full_context(
                task="Verify the ladder calibration",
                include_puzzles=[29, 30, 69, 70, 75, 80]
            )

        elif task_type == 'generate':
            return build_full_context(
                task="Generate puzzle using the calibrated ladder",
                include_puzzles=[69, 70]
            )

        else:
            # General context
            return build_full_context(include_puzzles=[70, 75, 80])

    def _extract_lane_number(self, message: str) -> Optional[int]:
        """Extract a lane number from the message if mentioned"""
        import re
        match = re.search(r'lane\s*(\d+)', message.lower())
        if match:
            lane = int(match.group(1))
            if 0 <= lane <= 15:
                return lane
        return None

    def _build_conversation_context(self, limit: int = 5) -> str:
        """Build recent conversation context"""
        if not self.conversation_history:
            return ""

        recent = self.conversation_history[-limit:]
        lines = ["## Recent Conversation:"]
        for msg in recent:
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:500] + "..." if len(msg['content']) > 500 else msg['content']
            lines.append(f"**{role}:** {content}")

        return '\n'.join(lines)

    def _handle_model_not_loaded(self, message: str) -> Dict:
        """Handle the case when model is not loaded - now using Ollama cloud models"""
        return {
            'message': """**Ollama Cloud Model Ready**

I'm using Ollama cloud models for mathematical reasoning.

Current model: **qwen2.5:72b**

I can:
- Compute drift constants using pure math
- Verify the ladder calibration  
- Generate puzzle (any unsolved)
- Explain the affine recurrence step by step

What would you like me to compute?

Examples:
- "Compute the drift for lane 5"
- "Verify the ladder from puzzle 29 to 70"
- "Generate puzzle"
- "Explain the affine recurrence formula\"""",
            'action_taken': 'model_status',
            'data': {'model_loaded': True, 'model_name': self.model_name}
        }


# Global agent instance
_agent: Optional[LadderAgent] = None


def get_agent() -> LadderAgent:
    """Get or create the global agent instance"""
    global _agent
    if _agent is None:
        _agent = LadderAgent()
    return _agent


def process_chat_message(message: str) -> Dict:
    """Process incoming chat message (API endpoint)"""
    agent = get_agent()
    return agent.process_message(message)


def get_conversation_history() -> List[Dict]:
    """Get conversation history"""
    agent = get_agent()
    return agent.conversation_history


def process_chat_message_with_rag(message: str, use_rag: bool = True) -> Dict:
    """Process chat message with optional RAG (memory + database context)"""
    agent = get_agent()

    if use_rag:
        # Build RAG context from memory system
        rag_context = agent.memory.build_context_summary()

        # Add database context if relevant
        try:
            import sqlite3
            import os
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kh-assist', 'db', 'kh.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()

                # Get puzzle count
                cur.execute("SELECT COUNT(*) FROM lcg_residuals")
                puzzle_count = cur.fetchone()[0]

                # Get some sample data if asking about puzzles
                message_lower = message.lower()
                if any(word in message_lower for word in ['puzzle', 'data', 'database', 'bits']):
                    cur.execute("SELECT bits, actual_hex FROM lcg_residuals ORDER BY bits LIMIT 5")
                    sample_puzzles = cur.fetchall()
                    rag_context += f"\n## Database Info:\n"
                    rag_context += f"- Total puzzles in database: {puzzle_count}\n"
                    rag_context += f"- Sample entries: {sample_puzzles}\n"

                conn.close()
        except Exception as e:
            rag_context += f"\n[Database access error: {e}]\n"

        # Prepend RAG context to the message processing
        agent._rag_context = rag_context
    else:
        agent._rag_context = ""

    return agent.process_message(message)


if __name__ == '__main__':
    print("=" * 60)
    print("Ladder Agent V2 - Model-First Architecture")
    print("=" * 60)

    agent = LadderAgent()

    print("\n📋 Testing task classification:")
    test_messages = [
        "compute the drift for lane 5",
        "verify the ladder",
        "generate puzzle",
        "what is the A matrix?",
        "hello, how are you?"
    ]

    for msg in test_messages:
        task = agent._classify_task(msg)
        print(f"  '{msg}' → {task}")

    print("\n📊 Testing context building:")
    print("\n--- Drift Context (Lane 5) ---")
    print(build_drift_computation_context(lane=5)[:1000])

    print("\n" + "=" * 60)
    print("Interactive mode (type 'quit' to exit)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if not user_input:
                continue

            response = agent.process_message(user_input)
            print(f"\n🤖 Agent ({response['action_taken']}):")
            print(response['message'])

        except KeyboardInterrupt:
            break

    print("\nGoodbye!")
