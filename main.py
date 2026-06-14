import logging
from router import orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("security_audit.log"), logging.StreamHandler()]
)

if __name__ == "__main__":
    print("\n=== AI Orchestrator Guardian (Synthesizer Version) ===\n")
    
    tasks = [
        # This task should trigger code execution and reporter analysis
        "Calculate the first 10 numbers of the Fibonacci sequence and state whether they are even or odd.",
        
        # This task should be routed directly to the reporter as text
        "In two sentences, briefly explain what the Python programming language is."
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n--- TESTING TASK {i} ---")
        print(f"User Request: {task}\n")
        
        final_output = orchestrator(task)
        
        print(f"\n[FINAL REPORT]:\n{final_output}\n")
        print("-" * 50)