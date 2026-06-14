import ollama
import logging
from broker import run_code_safely

logger = logging.getLogger("AgenticSandbox")

def solve_with_retry(task, max_retries=3):
    """Generates code, runs it in the sandbox, and returns RAW terminal output."""
    current_context = ""
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} started.")
        
        # Very restrictive instruction enforcing CLEAN code with print statements
        system_instruction = (
            "You are an Expert Python Developer. Write raw Python code to solve the task. "
            "Return ONLY executable code. No explanations. No markdown formatting blocks. "
            "You MUST print the final result using print() so it can be captured by standard output."
        )
        full_prompt = f"{system_instruction}\n\nTask: {task}\n{current_context}"
        
        try:
            response = ollama.generate(model='llama3.1', prompt=full_prompt)
            clean_code = response['response'].strip().replace("```python", "").replace("```", "").strip()
            
            result = run_code_safely(clean_code)
            
            if any(err in result for err in ["Security Constraint Violated", "Error:", "SyntaxError", "Exception", "Traceback"]):
                logger.warning(f"Execution failed: {result}")
                current_context = f"Previous code failed with this error:\n{result}\nPlease fix it."
            else:
                logger.info("Code executed successfully.")
                # Returning CLEAN, raw output from the container
                return result

        except Exception as e:
            logger.error(f"Fatal agent error: {str(e)}")
            break

    return "Task failed within security constraints."