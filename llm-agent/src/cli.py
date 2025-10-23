"""
Command Line Interface for Longevity Research LLM Agent

Provides an interactive chat interface to query the agent from the terminal.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from agent import LongevityAgent


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 80)
    print("LONGEVITY RESEARCH LLM AGENT".center(80))
    print("=" * 80)
    print("\nAsk questions about genes, proteins, aging, and evolution!")
    print("Type 'quit', 'exit', or 'q' to exit")
    print("Type 'reset' to clear conversation history")
    print("Type 'help' for example queries\n")
    print("=" * 80 + "\n")


def print_help():
    """Print example queries."""
    examples = [
        "What pathways is TP53 involved in?",
        "Show me the phylogenetic tree for human, chimp, and mouse",
        "What is the role of FOXO3 in the Horvath aging clock?",
        "Get the protein sequence for SIRT1 in human",
        "What drugs target EGFR?",
        "Tell me about longevity in naked mole rats",
        "Create a TP53 R175H mutation and save it to a file",
        "What is the GO annotation for BRCA1?",
    ]
    
    print("\nExample Queries:")
    print("-" * 80)
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    print("-" * 80 + "\n")


def main():
    """Run interactive CLI."""
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY environment variable not set")
        print("\nPlease set it using:")
        print("  PowerShell: $env:OPENAI_API_KEY = \"your-api-key\"")
        print("  Bash:       export OPENAI_API_KEY=\"your-api-key\"")
        print()
        sys.exit(1)
    
    # Initialize agent
    try:
        print("\nInitializing agent...")
        agent = LongevityAgent()
        print("Agent ready!")
    except Exception as e:
        print(f"\nFailed to initialize agent: {e}")
        sys.exit(1)
    
    print_header()
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!\n")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                print("\nConversation history cleared!\n")
                continue
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Get agent response
            print("\nAgent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            continue


if __name__ == "__main__":
    main()
