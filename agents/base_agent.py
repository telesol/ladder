#!/usr/bin/env python3
"""
Base Agent - Foundation for all Ladder Agents
Handles communication with Ollama Cloud API
"""
import os
import json
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml

class BaseAgent(ABC):
    """Base class for all ladder agents"""

    def __init__(self, agent_name: str, config_path: str = "config/config.yaml"):
        self.agent_name = agent_name
        self.config = self._load_config(config_path)
        self.agent_config = self.config['agents'].get(agent_name, {})
        self.base_url = self.config['agents']['base_url']
        self.api_key = os.getenv(self.config['agents']['api_key_env'])
        self.model = self.agent_config.get('model', 'qwen2.5:72b')
        self.temperature = self.agent_config.get('temperature', 0.7)
        self.max_tokens = self.agent_config.get('max_tokens', 4096)
        self.role = self.agent_config.get('role', 'General assistant')
        self.history: List[Dict] = []

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        # Handle relative path from project root
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, config_path)

        with open(config_path) as f:
            return yaml.safe_load(f)

    async def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Call Ollama Cloud API"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add history for context
        messages.extend(self.history[-10:])  # Last 10 messages
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

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
                        assistant_message = result.get('message', {}).get('content', '')
                    except json.JSONDecodeError:
                        assistant_message = text_response

                    # Update history
                    self.history.append({"role": "user", "content": prompt})
                    self.history.append({"role": "assistant", "content": assistant_message})

                    return assistant_message
                else:
                    error = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error}")

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return f"""You are {self.agent_name}, a specialized AI agent for the Bitcoin Puzzle Ladder project.

Your role: {self.role}

You have access to:
- kh.db: Database with puzzle data (lcg_residuals table)
- Calibration data: Affine recurrence parameters (A matrix, drift constants)
- Training data: Historical discoveries and learnings

Mathematical Model:
- Each lane follows: y = A[l] * x + C[k][l][occ] (mod 256)
- 16 parallel lanes (l = 0 to 15)
- A[l] = multiplier for lane l
- C[k][l][occ] = drift constant for block k, lane l, occurrence occ

CRITICAL RULES:
1. NO STUBS - Always compute full mathematical values
2. NO HARDCODING - Derive everything from the model
3. VERIFY EVERYTHING - Use cryptographic proofs
4. PURE MATH - Show all steps, no shortcuts

Output format: JSON when returning data, markdown for explanations."""

    @abstractmethod
    async def execute(self, task: Dict) -> Dict:
        """Execute a task - must be implemented by subclasses"""
        pass

    async def think(self, prompt: str) -> str:
        """Think about a problem and return reasoning"""
        return await self._call_ollama(prompt, self.get_system_prompt())

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{self.agent_name}] [{level}] {message}")

    def save_discovery(self, category: str, title: str, content: str,
                       confidence: float = 0.5, verified: bool = False) -> Dict:
        """Save a discovery to be recorded in the database"""
        return {
            "type": "discovery",
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "category": category,
            "title": title,
            "content": content,
            "confidence": confidence,
            "verified": verified
        }
