#!/usr/bin/env python3
"""
Ladder Model - Load the fine-tuned Qwen2.5-72B with LoRA adapter

This module loads the TRAINED model with all the ladder mathematics knowledge.
The LoRA adapter at ladder_lora_model/final/ contains the fine-tuned weights.
"""
import os
import json
from typing import Optional, List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LORA_PATH = os.path.join(BASE_DIR, 'ladder_lora_model', 'final')
CONFIG_PATH = os.path.join(BASE_DIR, 'model_config.json')


class LadderModel:
    """The fine-tuned ladder AI model"""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = None
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load model configuration"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                return json.load(f)
        return {}

    def load(self) -> bool:
        """Load the model with LoRA adapter"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            from peft import PeftModel

            print("=" * 60)
            print("Loading Bitcoin Puzzle Ladder AI Model")
            print("=" * 60)

            # Check for LoRA adapter
            if not os.path.exists(LORA_PATH):
                print(f"❌ LoRA adapter not found at: {LORA_PATH}")
                return False

            adapter_config_path = os.path.join(LORA_PATH, 'adapter_config.json')
            if not os.path.exists(adapter_config_path):
                print(f"❌ adapter_config.json not found")
                return False

            # Read adapter config to get base model
            with open(adapter_config_path) as f:
                adapter_config = json.load(f)

            base_model_name = adapter_config.get('base_model_name_or_path', 'Qwen/Qwen2.5-72B-Instruct')
            print(f"Base model: {base_model_name}")
            print(f"LoRA adapter: {LORA_PATH}")

            # Configure 4-bit quantization
            print("\nConfiguring 4-bit quantization...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            # Load tokenizer from LoRA path (has the trained tokenizer)
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                LORA_PATH,
                trust_remote_code=True
            )

            # Load base model with quantization
            print("Loading base model (this may take several minutes)...")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

            # Load LoRA adapter
            print("Loading LoRA adapter...")
            self.model = PeftModel.from_pretrained(
                base_model,
                LORA_PATH,
                is_trainable=False
            )

            self.model.eval()
            self.is_loaded = True
            self.device = next(self.model.parameters()).device

            # Memory stats
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1e9
                reserved = torch.cuda.memory_reserved() / 1e9
                print(f"\n✅ Model loaded successfully!")
                print(f"   GPU Memory: {allocated:.2f} GB allocated, {reserved:.2f} GB reserved")
            else:
                print(f"\n✅ Model loaded on CPU")

            return True

        except ImportError as e:
            print(f"❌ Missing dependencies: {e}")
            print("   Install with: pip install transformers torch accelerate bitsandbytes peft")
            return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        show_thinking: bool = True
    ) -> Optional[str]:
        """Generate a response from the model

        Args:
            prompt: The user's message/question
            system_prompt: System prompt guiding behavior
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (low = more deterministic)
            show_thinking: Whether to show generation progress

        Returns:
            The model's response or None on error
        """
        if not self.is_loaded:
            print("❌ Model not loaded. Call load() first.")
            return None

        try:
            import torch

            # Use default system prompt if not provided
            if system_prompt is None:
                system_prompt = self.config.get('system_prompt',
                    "You are a mathematical reasoning AI. Compute step by step.")

            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            # Apply chat template
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Tokenize
            inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

            if show_thinking:
                print("🤔 Thinking...")

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature if temperature > 0 else None,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # Decode only the new tokens
            new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

            return response.strip()

        except Exception as e:
            print(f"❌ Generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def reason(
        self,
        task: str,
        context: str,
        system_prompt: str = None,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """Perform mathematical reasoning with full context

        Args:
            task: What the model should do
            context: Mathematical context (calibration data, puzzle values)
            system_prompt: System prompt for behavior guidance
            max_tokens: Maximum response length

        Returns:
            The model's reasoning and computation
        """
        # Combine context and task into a single prompt
        full_prompt = f"""{context}

---

## Your Task

{task}

Show your work step by step. Perform all arithmetic yourself.
"""

        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.1  # Low temperature for deterministic math
        )

    def unload(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.is_loaded = False

            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass

            print("✅ Model unloaded")


# Global instance
_ladder_model: Optional[LadderModel] = None


def get_ladder_model() -> LadderModel:
    """Get or create the global ladder model instance"""
    global _ladder_model
    if _ladder_model is None:
        _ladder_model = LadderModel()
    return _ladder_model


def is_model_loaded() -> bool:
    """Check if model is currently loaded"""
    model = get_ladder_model()
    return model.is_loaded


def load_model() -> bool:
    """Load the model"""
    model = get_ladder_model()
    return model.load()


def generate(prompt: str, **kwargs) -> Optional[str]:
    """Generate a response"""
    model = get_ladder_model()
    if not model.is_loaded:
        if not model.load():
            return None
    return model.generate(prompt, **kwargs)


def reason(task: str, context: str, **kwargs) -> Optional[str]:
    """Perform reasoning with context"""
    model = get_ladder_model()
    if not model.is_loaded:
        if not model.load():
            return None
    return model.reason(task, context, **kwargs)


if __name__ == '__main__':
    print("=" * 60)
    print("Ladder Model Test")
    print("=" * 60)

    model = LadderModel()

    print("\nChecking LoRA adapter files...")
    if os.path.exists(LORA_PATH):
        files = os.listdir(LORA_PATH)
        print(f"✅ Found {len(files)} files in {LORA_PATH}")
        for f in files:
            size = os.path.getsize(os.path.join(LORA_PATH, f)) / 1e6
            print(f"   - {f}: {size:.1f} MB")
    else:
        print(f"❌ LoRA path not found: {LORA_PATH}")

    # Ask user if they want to load
    response = input("\n⚠️  Load the model? This requires ~40GB VRAM. (y/N): ")
    if response.lower() == 'y':
        if model.load():
            # Test with a simple math question
            test_prompt = """Given:
- A[5] = 169
- X_75[5] = 76 (0x4c)
- X_80[5] = 224 (0xe0)

Compute C_0[5] using the 5-step affine recurrence formula.
Show all arithmetic steps."""

            print("\n" + "=" * 60)
            print("Test prompt:")
            print(test_prompt)
            print("=" * 60)

            response = model.generate(test_prompt, max_tokens=1024)
            print("\n🤖 Model Response:")
            print(response)

            model.unload()
