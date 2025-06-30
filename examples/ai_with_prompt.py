"""
Example demonstrating AI Service usage with external prompt files.

This example shows how to:
1. Load external prompt files using TextReader
2. Use the AI service with different configurations
3. Combine system prompts with user queries
4. Handle errors gracefully
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from utils
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils import AIService, text_reader, quick_query


def demo_ai_with_external_prompt():
    """Demonstrate using AI service with external prompt files."""
    
    print("=== AI Service with External Prompts Demo ===")
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment variables")
        print("Please set your OpenAI API key to run this example")
        return
    
    # 1. Load external prompt file
    print("\n1. Loading external prompt file...")
    try:
        btt_prompt = text_reader.read_file("prompts/btt_prompt.txt")
        print(f"✅ Loaded BTT prompt ({len(btt_prompt)} characters)")
        print(f"Preview: {btt_prompt[:150]}...")
    except Exception as e:
        print(f"❌ Failed to load prompt file: {e}")
        return
    
    # 2. Initialize AI service with external prompt as system message
    print("\n2. Initializing AI service with external prompt...")
    try:
        ai_service = AIService(
            model="gpt-4o-mini",  # Using mini for cost efficiency in demo
            temperature=0.7,
            max_tokens=500,
            system_message=btt_prompt
        )
        print("✅ AI service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI service: {e}")
        return
    
    # 3. Example queries using the BTT assistant
    example_queries = [
        "How do I create a three-finger swipe gesture to switch between desktops?",
        "What's the best way to set up window snapping shortcuts?",
        "Help me create an AppleScript to toggle Wi-Fi when I press Cmd+Option+W"
    ]
    
    print("\n3. Running example queries...")
    for i, query in enumerate(example_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Question: {query}")
        
        try:
            response = ai_service.simple_query(query)
            print(f"Response: {response[:200]}...")
            if len(response) > 200:
                print("[Response truncated for demo]")
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    # 4. Demonstrate updating configuration
    print("\n4. Updating AI service configuration...")
    try:
        ai_service.update_config(
            temperature=0.3,  # More deterministic responses
            max_tokens=300
        )
        print("✅ Configuration updated (lower temperature, fewer tokens)")
        
        # Test with updated config
        response = ai_service.simple_query("Give me a quick tip for BetterTouchTool beginners")
        print(f"Quick tip: {response}")
    except Exception as e:
        print(f"❌ Configuration update failed: {e}")


def demo_multiple_prompt_files():
    """Demonstrate using multiple prompt files for different contexts."""
    
    print("\n=== Multiple Prompt Files Demo ===")
    
    # Create different AI assistants for different purposes
    prompt_configs = {
        "btt_assistant": {
            "prompt_file": "prompts/btt_prompt.txt",
            "description": "BetterTouchTool specialist"
        }
        # You can add more prompt files here:
        # "code_assistant": {
        #     "prompt_file": "prompts/code_prompt.txt", 
        #     "description": "Code review specialist"
        # }
    }
    
    assistants = {}
    
    # Load each assistant
    for name, config in prompt_configs.items():
        try:
            prompt_content = text_reader.read_file(config["prompt_file"])
            assistants[name] = {
                "service": AIService(
                    model="gpt-4o-mini",
                    temperature=0.7,
                    system_message=prompt_content
                ),
                "description": config["description"]
            }
            print(f"✅ Loaded {name}: {config['description']}")
        except Exception as e:
            print(f"❌ Failed to load {name}: {e}")
    
    # Test each assistant
    if assistants:
        print(f"\n📋 Available assistants: {list(assistants.keys())}")
        
        # Example usage
        if "btt_assistant" in assistants:
            try:
                response = assistants["btt_assistant"]["service"].simple_query(
                    "What's one essential BetterTouchTool feature every Mac user should know?"
                )
                print(f"\nBTT Assistant says: {response}")
            except Exception as e:
                print(f"❌ BTT Assistant query failed: {e}")


def demo_quick_query_with_prompts():
    """Demonstrate using the quick_query function with custom prompts."""
    
    print("\n=== Quick Query with Custom Prompts Demo ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY required for quick query demo")
        return
    
    # Load prompt for system message
    try:
        custom_prompt = text_reader.read_file_safe(
            "prompts/btt_prompt.txt", 
            "You are a helpful assistant specializing in macOS automation."
        )
        
        # Use quick_query with custom system message
        response = quick_query(
            "Explain what BetterTouchTool is in one sentence",
            system_message=custom_prompt,
            model="gpt-4o-mini",
            temperature=0.5
        )
        
        print(f"Quick query response: {response}")
        
    except Exception as e:
        print(f"❌ Quick query failed: {e}")


def main():
    """Run all AI service demonstrations."""
    
    print("🤖 AI Service with External Prompts Examples")
    print("=" * 50)
    
    # Run the main demo
    demo_ai_with_external_prompt()
    
    # Run multiple prompts demo
    demo_multiple_prompt_files()
    
    # Run quick query demo
    demo_quick_query_with_prompts()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\n💡 Tips:")
    print("- Set OPENAI_API_KEY environment variable to run live queries")
    print("- Create more prompt files in the 'prompts/' directory")
    print("- Adjust temperature and max_tokens for different use cases")
    print("- Use images parameter for vision-enabled queries")


if __name__ == "__main__":
    main()
