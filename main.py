import logging
import argparse
import sys
from router import orchestrator

# Global logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("security_audit.log"), logging.StreamHandler()]
)

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="AI Sandbox Guardian - Multi-Agent Orchestrator")
    parser.add_argument(
        "query", 
        type=str, 
        nargs="?", 
        help="The task or question you want to send to the AI"
    )
    
    args = parser.parse_args()

    print("\n=== AI Orchestrator Guardian (Synthesizer Version) ===\n")

    # Check if the user provided a query
    if not args.query:
        print("Error: No query provided.")
        print('Usage example: python3 main.py "Calculate the first 10 numbers of the Fibonacci sequence"')
        sys.exit(1)
        
    task = args.query
    
    print("--- PROCESSING TASK ---")
    print(f"User Request: {task}\n")
    
    # Run the orchestrator with the provided CLI argument
    final_output = orchestrator(task)
    
    print(f"\n[FINAL REPORT]:\n{final_output}\n")
    print("-" * 50)