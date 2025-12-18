#!/usr/bin/env python3
"""
Ollama Integration Module with Token Management
Provides unified interface for calling Ollama models with model selection and token optimization
"""
import os
import json
import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import logging

# Import token manager
from token_manager import get_token_manager, TokenManager

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY', '')
        self.timeout = 120  # Reduced from 5 minutes to 2 minutes to prevent timeouts
        
    async def list_models(self) -> List[Dict]:
        """List available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                async with session.get(
                    f"{self.base_url}/api/tags",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('models', [])
                    else:
                        error_text = await response.text()
                        print(f"Error listing models: {response.status} - {error_text}")
                        return []
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return []
    
    async def generate(self, model: str, prompt: str, system: str = None, 
                      max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate response from Ollama model with token management"""
        try:
            # Get token manager for this model
            token_manager = get_token_manager(model, max_tokens)
            
            # Optimize prompt if too large
            original_tokens = token_manager.count_tokens(prompt)
            if original_tokens > max_tokens * 0.8:  # 80% of max to leave room for response
                logger.warning(f"Prompt too large: {original_tokens} tokens, optimizing...")
                prompt = token_manager.optimize_prompt(prompt, max_tokens=max_tokens * 0.7)
                optimized_tokens = token_manager.count_tokens(prompt)
                logger.info(f"Optimized prompt from {original_tokens} to {optimized_tokens} tokens")
            
            # Optimize system prompt if provided
            if system:
                system_tokens = token_manager.count_tokens(system)
                if system_tokens > max_tokens * 0.2:  # System prompt shouldn't exceed 20%
                    logger.warning(f"System prompt too large: {system_tokens} tokens")
                    system = token_manager.optimize_prompt(system, max_tokens=max_tokens * 0.15)
            
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    },
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        text_response = await response.text()
                        try:
                            result = json.loads(text_response)
                            response_text = result.get('response', '')
                            
                            # Monitor token usage
                            usage_info = token_manager.monitor_token_usage(
                                prompt, response_text, f"generate_{model}"
                            )
                            
                            return response_text
                        except json.JSONDecodeError:
                            return text_response
                    else:
                        error_text = await response.text()
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    async def chat(self, model: str, messages: List[Dict], 
                   max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Chat with Ollama model using conversation history with token management"""
        try:
            # Get token manager for this model
            token_manager = get_token_manager(model, max_tokens)
            
            # Optimize messages if too large
            original_tokens = token_manager.count_tokens_in_messages(messages)
            if original_tokens > max_tokens * 0.8:  # 80% of max to leave room for response
                logger.warning(f"Chat messages too large: {original_tokens} tokens, optimizing...")
                messages = token_manager.optimize_messages(messages, max_tokens=max_tokens * 0.7)
                optimized_tokens = token_manager.count_tokens_in_messages(messages)
                logger.info(f"Optimized messages from {original_tokens} to {optimized_tokens} tokens")
            
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/api/chat",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        # Handle both JSON and text/plain responses (Ollama sometimes returns text/plain)
                        text_response = await response.text()
                        try:
                            result = json.loads(text_response)
                            response_text = result.get('message', {}).get('content', '')
                        except json.JSONDecodeError:
                            # If not valid JSON, use raw text
                            response_text = text_response

                        # Monitor token usage
                        # Reconstruct full prompt from messages for monitoring
                        full_prompt = '\n'.join([msg.get('content', '') for msg in messages])
                        usage_info = token_manager.monitor_token_usage(
                            full_prompt, response_text, f"chat_{model}"
                        )

                        return response_text
                    else:
                        error_text = await response.text()
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error in chat: {str(e)}"

# Global client instance
_ollama_client: Optional[OllamaClient] = None

def get_ollama_client() -> OllamaClient:
    """Get or create global Ollama client"""
    global _ollama_client
    if _ollama_client is None:
        # Use local endpoint by default, fallback to cloud if configured
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        api_key = os.getenv("OLLAMA_API_KEY")
        _ollama_client = OllamaClient(base_url=base_url, api_key=api_key)
    return _ollama_client

async def list_ollama_models() -> List[Dict]:
    """List available Ollama models"""
    client = get_ollama_client()
    return await client.list_models()

async def generate_with_ollama(model: str, prompt: str, system: str = None,
                              max_tokens: int = 2048, temperature: float = 0.7) -> str:
    """Generate response with specific Ollama model"""
    client = get_ollama_client()
    return await client.generate(model, prompt, system, max_tokens, temperature)

async def chat_with_ollama(model: str, messages: List[Dict],
                          max_tokens: int = 2048, temperature: float = 0.7) -> str:
    """Chat with Ollama model using conversation history"""
    client = get_ollama_client()
    return await client.chat(model, messages, max_tokens, temperature)

# Synchronous wrappers for Flask compatibility
def list_ollama_models_sync() -> List[Dict]:
    """Synchronous wrapper to list Ollama models"""
    try:
        return asyncio.run(list_ollama_models())
    except Exception as e:
        print(f"Error listing Ollama models: {e}")
        return []

def generate_with_ollama_sync(model: str, prompt: str, system: str = None,
                             max_tokens: int = 2048, temperature: float = 0.7) -> str:
    """Synchronous wrapper to generate with Ollama"""
    try:
        return asyncio.run(generate_with_ollama(model, prompt, system, max_tokens, temperature))
    except Exception as e:
        return f"Error generating with Ollama: {str(e)}"

def chat_with_ollama_sync(model: str, messages: List[Dict],
                         max_tokens: int = 2048, temperature: float = 0.7) -> str:
    """Synchronous wrapper to chat with Ollama"""
    try:
        return asyncio.run(chat_with_ollama(model, messages, max_tokens, temperature))
    except Exception as e:
        return f"Error chatting with Ollama: {str(e)}"

if __name__ == '__main__':
    print("Testing Ollama Integration...")
    
    # Test listing models
    print("\nAvailable models:")
    models = list_ollama_models_sync()
    for model in models:
        print(f"  - {model.get('name', 'Unknown')}")
    
    # Test generation
    if models:
        test_model = models[0]['name']
        print(f"\nTesting generation with {test_model}...")
        response = generate_with_ollama_sync(test_model, "What is 2+2?")
        print(f"Response: {response}")
