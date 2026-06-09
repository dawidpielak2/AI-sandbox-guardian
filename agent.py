import ollama
import logging
from broker import run_code_safely

# Setup dual logging (file + console) for security auditing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("security_audit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AgenticSandbox")

def solve_with_retry(task, max_retries=3):
    """Attempts to solve a task using LLM, featuring a self-healing error loop."""
    current_context = ""
    logger.info(f"New Task Received: {task}")

    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} started.")
        
        system_instruction = (
            "You are a Python Security Engineer. Write raw Python code to solve the task. "
            "Return ONLY code. No explanations. No markdown blocks. "
            "If you receive an error message, analyze and fix your code."
        )
        
        full_prompt = f"{system_instruction}\n\nTask: {task}\n{current_context}"
        
        try:
            response = ollama.generate(model='llama3.1', prompt=full_prompt)
            
            # Sanitize LLM output from markdown artifacts
            clean_code = response['response'].strip().replace("```python", "").replace("```", "").strip()
            logger.info(f"Code generated. Length: {len(clean_code)} chars.")
            
            result = run_code_safely(clean_code)
            
            # Evaluate sandbox execution outcome
            if any(err in result for err in ["Security Constraint Violated", "Security/Execution Error", "SyntaxError", "Exception"]):
                logger.warning(f"Execution failed: {result}")
                current_context = f"Previous code failed with this error:\n{result}\nPlease fix it."
            else:
                logger.info("Task completed successfully.")
                return result

        except Exception as e:
            logger.error(f"Fatal agent error: {str(e)}")
            break

    logger.error("Max retries reached.")
    return "Task failed within security constraints."

if __name__ == "__main__":
    print("\n=== AI Sandbox Guardian Agent ===\n")
    user_query = "Calculate the first 10 numbers of the Fibonacci sequence and print them."
    final_output = solve_with_retry(user_query)
    print(f"\n[FINAL RESULT]:\n{final_output}")