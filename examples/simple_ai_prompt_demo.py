"""
Simple demonstration of using AI Service with external prompts.

This is a minimal example showing the core pattern:
1. Load prompt file with TextReader
2. Initialize AI service with the prompt
3. Query the AI
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from utils
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils import AIService, text_reader


def simple_demo():
    """Simple demonstration of the AI + TextReader workflow."""
    
    print("🤖 Simple AI + TextReader Demo")
    print("-" * 40)
    
    # Step 1: Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   You can get one from: https://platform.openai.com/api-keys")
        return
    
    # Step 2: Load external prompt
    print("📖 Loading prompt file...")
    try:
        prompt = text_reader.read_file("prompts/btt_prompt.txt")
        print(f"✅ Loaded prompt ({len(prompt)} characters)")
    except Exception as e:
        print(f"❌ Failed to load prompt: {e}")
        return
    
    # Step 3: Initialize AI with the prompt
    print("🧠 Initializing AI service...")
    try:
        ai = AIService(
            model="gpt-4o-mini",  # Cost-effective for demos
            temperature=0.7,
            system_message=prompt
        )
        print("✅ AI service ready")
    except Exception as e:
        print(f"❌ Failed to initialize AI: {e}")
        return
    
    # Step 4: Ask a question
    print("💬 Asking AI a question...")
    question = "What is BetterTouchTool and why should I use it?"
    
    try:
        answer = ai.simple_query(question)
        print(f"\n📝 Question: {question}")
        print(f"🤖 Answer: {answer}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    simple_demo() 