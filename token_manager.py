#!/usr/bin/env python3
"""
Token Management System for Autonomous Agents
Handles token limits, prompt optimization, and intelligent data chunking
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Fallback for tiktoken if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using character-based estimation")

logger = logging.getLogger(__name__)

@dataclass
class TokenLimits:
    """Token limits for different models"""
    mistral_large = 128000  # 128k context window
    qwen_72b = 32768        # 32k context window
    gpt_4 = 8192            # 8k context window
    gpt_3_5 = 4096          # 4k context window

@dataclass
class TokenBudget:
    """Token budget allocation for different operations"""
    system_prompt = 1000
    context = 2000
    user_input = 1000
    response_buffer = 1000
    safety_margin = 500

class TokenManager:
    """Manages token limits and optimizes prompts for AI models"""
    
    def __init__(self, model_name: str = "mistral-large", max_tokens: int = None):
        self.model_name = model_name
        self.max_tokens = max_tokens or self._get_model_limit(model_name)
        self.encoding = self._get_encoding(model_name)
        self.token_budget = TokenBudget()
        
        logger.info(f"TokenManager initialized for {model_name} with {self.max_tokens} max tokens")
    
    def _get_model_limit(self, model_name: str) -> int:
        """Get token limit for specific model"""
        limits = {
            'mistral-large': TokenLimits.mistral_large,
            'mistral-large-3': TokenLimits.mistral_large,
            'qwen2.5:72b': TokenLimits.qwen_72b,
            'qwen2.5': TokenLimits.qwen_72b,
            'gpt-4': TokenLimits.gpt_4,
            'gpt-3.5': TokenLimits.gpt_3_5,
        }
        
        # Check for partial matches
        for key, limit in limits.items():
            if key in model_name.lower():
                return limit
        
        return TokenLimits.gpt_4  # Default fallback
    
    def _get_encoding(self, model_name: str):
        """Get appropriate tokenizer encoding"""
        if not TIKTOKEN_AVAILABLE:
            # Fallback to simple character counting
            class SimpleEncoding:
                def encode(self, text):
                    return list(text.encode('utf-8'))
                def decode(self, tokens):
                    return bytes(tokens).decode('utf-8', errors='ignore')
            return SimpleEncoding()
        
        try:
            # Try to use tiktoken for OpenAI models
            if 'gpt' in model_name.lower():
                return tiktoken.encoding_for_model(model_name)
            else:
                # Fallback to cl100k_base for most models
                return tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Error getting tiktoken encoding: {e}")
            # Final fallback
            class SimpleEncoding:
                def encode(self, text):
                    return list(text.encode('utf-8'))
                def decode(self, tokens):
                    return bytes(tokens).decode('utf-8', errors='ignore')
            return SimpleEncoding()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4
    
    def count_tokens_in_messages(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of messages"""
        total_tokens = 0
        for message in messages:
            # Count role, content, and some overhead
            total_tokens += self.count_tokens(message.get('role', ''))
            total_tokens += self.count_tokens(message.get('content', ''))
            total_tokens += 10  # Message overhead
        return total_tokens + 10  # Additional overhead
    
    def optimize_prompt(self, prompt: str, max_tokens: int = None, 
                       priority_sections: List[str] = None) -> str:
        """Optimize prompt to fit within token limits"""
        if max_tokens is None:
            max_tokens = self.max_tokens - self.token_budget.safety_margin
        
        current_tokens = self.count_tokens(prompt)
        
        if current_tokens <= max_tokens:
            return prompt
        
        logger.warning(f"Prompt too large: {current_tokens} tokens, max: {max_tokens}")
        
        # Try different optimization strategies
        optimized = self._truncate_prompt(prompt, max_tokens, priority_sections)
        
        if self.count_tokens(optimized) <= max_tokens:
            return optimized
        
        # If still too large, use more aggressive optimization
        optimized = self._summarize_prompt(prompt, max_tokens)
        
        return optimized
    
    def _truncate_prompt(self, prompt: str, max_tokens: int, 
                        priority_sections: List[str] = None) -> str:
        """Truncate prompt intelligently"""
        lines = prompt.split('\n')
        current_tokens = self.count_tokens(prompt)
        
        if priority_sections:
            # Keep priority sections, truncate others
            kept_lines = []
            other_lines = []
            
            for line in lines:
                if any(section in line.lower() for section in priority_sections):
                    kept_lines.append(line)
                else:
                    other_lines.append(line)
            
            # Start with priority sections
            result = '\n'.join(kept_lines)
            
            # Add other lines until we hit the limit
            for line in other_lines:
                test_result = result + '\n' + line
                if self.count_tokens(test_result) <= max_tokens:
                    result = test_result
                else:
                    break
            
            return result
        else:
            # Simple truncation from the end
            truncated_lines = []
            current_tokens = 0
            
            for line in lines:
                line_tokens = self.count_tokens(line)
                if current_tokens + line_tokens <= max_tokens:
                    truncated_lines.append(line)
                    current_tokens += line_tokens
                else:
                    break
            
            return '\n'.join(truncated_lines)
    
    def _summarize_prompt(self, prompt: str, max_tokens: int) -> str:
        """Create a summary of the prompt"""
        # Simple summarization strategy
        lines = prompt.split('\n')
        
        # Keep first few lines (introduction)
        intro_lines = lines[:5]
        
        # Keep last few lines (conclusion)
        conclusion_lines = lines[-5:] if len(lines) > 10 else []
        
        # Keep middle section headers
        middle_lines = [line for line in lines[5:-5] if line.strip().startswith('#')]
        
        summary_lines = intro_lines + middle_lines + conclusion_lines
        
        # Ensure we stay within token limit
        result = '\n'.join(summary_lines)
        while self.count_tokens(result) > max_tokens and len(summary_lines) > 3:
            summary_lines = summary_lines[:-2] + summary_lines[-1:]  # Remove middle content
            result = '\n'.join(summary_lines)
        
        return result
    
    def chunk_data(self, data: List[Dict[str, Any]], 
                   chunk_size: int = None, 
                   overlap: int = 0) -> List[List[Dict[str, Any]]]:
        """Chunk large data into manageable pieces"""
        if chunk_size is None:
            # Calculate chunk size based on token budget
            chunk_size = 50  # Default chunk size
        
        chunks = []
        
        for i in range(0, len(data), chunk_size - overlap):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def optimize_messages(self, messages: List[Dict[str, str]], 
                         max_tokens: int = None) -> List[Dict[str, str]]:
        """Optimize message list to fit within token limits"""
        if max_tokens is None:
            max_tokens = self.max_tokens - self.token_budget.safety_margin
        
        current_tokens = self.count_tokens_in_messages(messages)
        
        if current_tokens <= max_tokens:
            return messages
        
        logger.warning(f"Messages too large: {current_tokens} tokens, max: {max_tokens}")
        
        # Try to optimize by removing older messages
        optimized_messages = messages.copy()
        
        # Keep system messages and recent user/assistant messages
        system_messages = [msg for msg in optimized_messages if msg.get('role') == 'system']
        other_messages = [msg for msg in optimized_messages if msg.get('role') != 'system']
        
        # Keep only recent messages
        while (self.count_tokens_in_messages(system_messages + other_messages) > max_tokens and 
               len(other_messages) > 2):
            # Remove oldest non-system message
            other_messages.pop(0)
        
        return system_messages + other_messages
    
    def create_intelligent_summary(self, data: Dict[str, Any], 
                                  max_tokens: int = None,
                                  focus_keys: List[str] = None) -> str:
        """Create intelligent summary of data"""
        if max_tokens is None:
            max_tokens = self.max_tokens // 4  # Use 25% of context for summary
        
        if focus_keys:
            # Focus on specific keys
            focused_data = {k: v for k, v in data.items() if k in focus_keys}
            summary_json = json.dumps(focused_data, indent=2, default=str)
        else:
            # Create general summary
            summary_data = {
                'data_size': len(str(data)),
                'key_count': len(data),
                'top_keys': list(data.keys())[:10],
                'has_nested_data': any(isinstance(v, dict) for v in data.values())
            }
            summary_json = json.dumps(summary_data, indent=2, default=str)
        
        # Ensure it fits in token limit
        if self.count_tokens(summary_json) > max_tokens:
            # Create even more condensed summary
            condensed_data = {
                'summary': f"{len(data)} items, {len(str(data))} characters",
                'keys': list(data.keys())[:5]
            }
            summary_json = json.dumps(condensed_data)
        
        return summary_json
    
    def split_large_analysis(self, analysis_data: Dict[str, Any], 
                           chunk_tokens: int = None) -> List[Dict[str, Any]]:
        """Split large analysis into manageable chunks"""
        if chunk_tokens is None:
            chunk_tokens = self.max_tokens // 2  # Use half context per chunk
        
        chunks = []
        current_chunk = {}
        current_tokens = 0
        
        for key, value in analysis_data.items():
            key_tokens = self.count_tokens(f"{key}: {str(value)[:100]}...")
            
            if current_tokens + key_tokens > chunk_tokens and current_chunk:
                # Start new chunk
                chunks.append(current_chunk)
                current_chunk = {}
                current_tokens = 0
            
            current_chunk[key] = value
            current_tokens += key_tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def create_progressive_context(self, base_context: str, 
                                 additional_data: List[Dict[str, Any]],
                                 max_tokens: int = None) -> List[str]:
        """Create progressively more detailed context"""
        if max_tokens is None:
            max_tokens = self.max_tokens - self.token_budget.safety_margin
        
        contexts = []
        current_context = base_context
        current_tokens = self.count_tokens(current_context)
        
        for data_item in additional_data:
            # Convert data to string
            data_str = json.dumps(data_item, indent=2, default=str)
            data_tokens = self.count_tokens(data_str)
            
            if current_tokens + data_tokens <= max_tokens:
                # Add to current context
                current_context += f"\n\n{data_str}"
                current_tokens += data_tokens
            else:
                # Save current context and start new one
                contexts.append(current_context)
                current_context = base_context + f"\n\n{data_str}"
                current_tokens = self.count_tokens(current_context)
        
        if current_context:
            contexts.append(current_context)
        
        return contexts
    
    def monitor_token_usage(self, prompt: str, response: str, 
                          operation: str = "unknown") -> Dict[str, Any]:
        """Monitor and log token usage"""
        prompt_tokens = self.count_tokens(prompt)
        response_tokens = self.count_tokens(response)
        total_tokens = prompt_tokens + response_tokens
        
        usage_info = {
            'operation': operation,
            'prompt_tokens': prompt_tokens,
            'response_tokens': response_tokens,
            'total_tokens': total_tokens,
            'model': self.model_name,
            'timestamp': datetime.now().isoformat(),
            'efficiency': response_tokens / max(prompt_tokens, 1),  # Response per prompt token
            'within_limits': total_tokens <= self.max_tokens
        }
        
        logger.info(f"Token usage for {operation}: {prompt_tokens} + {response_tokens} = {total_tokens} tokens")
        
        if not usage_info['within_limits']:
            logger.warning(f"Token limit exceeded for {operation}: {total_tokens} > {self.max_tokens}")
        
        return usage_info
    
    def get_optimization_suggestions(self, prompt: str, max_tokens: int = None) -> List[str]:
        """Get suggestions for optimizing prompts"""
        current_tokens = self.count_tokens(prompt)
        target_tokens = max_tokens or (self.max_tokens - self.token_budget.safety_margin)
        
        suggestions = []
        
        if current_tokens > target_tokens:
            overflow_ratio = current_tokens / target_tokens
            
            if overflow_ratio > 2:
                suggestions.append("Consider breaking into multiple smaller prompts")
                suggestions.append("Use progressive context building instead of single large prompt")
            
            suggestions.append(f"Current prompt is {current_tokens} tokens, target is {target_tokens}")
            suggestions.append("Remove redundant or less important information")
            suggestions.append("Use bullet points instead of full sentences where possible")
            suggestions.append("Consider using data summaries instead of full datasets")
            
            # Analyze prompt structure
            lines = prompt.split('\n')
            if len(lines) > 100:
                suggestions.append(f"Prompt has {len(lines)} lines - consider structural simplification")
            
            # Check for repetitive content
            unique_lines = set(line.strip() for line in lines if line.strip())
            if len(unique_lines) < len(lines) * 0.7:
                suggestions.append("Remove duplicate or highly similar content")
        
        return suggestions

# Global token manager instance
_token_manager = None

def get_token_manager(model_name: str = "mistral-large", max_tokens: int = None) -> TokenManager:
    """Get or create global token manager"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager(model_name, max_tokens)
    return _token_manager

if __name__ == "__main__":
    # Test the token manager
    logging.basicConfig(level=logging.INFO)
    
    print("🧮 Testing Token Manager")
    print("=" * 50)
    
    manager = TokenManager("mistral-large")
    
    # Test token counting
    test_text = "Hello, this is a test prompt for token counting."
    tokens = manager.count_tokens(test_text)
    print(f"Test text tokens: {tokens}")
    
    # Test optimization
    large_text = "This is a very long prompt " * 1000
    optimized = manager.optimize_prompt(large_text, max_tokens=100)
    print(f"Optimized prompt tokens: {manager.count_tokens(optimized)}")
    
    # Test suggestions
    suggestions = manager.get_optimization_suggestions(large_text, max_tokens=100)
    print(f"Optimization suggestions: {len(suggestions)}")
    
    print("✅ Token manager tests complete!")
