import ollama
import logging
from broker import run_code_safely
from config import MODEL_NAME

logger = logging.getLogger("AgenticSandbox")

def solve_with_retry(chat_history, quarantine_dir=None, max_retries=3):
    """Writes code, runs it, and repeats if there is an error."""
    current_error_context = ""
    
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} started.")
        system_instruction = (
            "You are an Expert Python Developer. Write raw Python code to solve the task. "
            "Return ONLY executable code. No explanations. No markdown formatting blocks. "
            "You MUST print the final result using print() so it can be captured by standard output. "
            "CRITICAL: When printing results, ALWAYS include a clear descriptive text label in the print statement "
            "(e.g., use print('The sum of the first 5 numbers is: 20') instead of just print(20)). "
            "This context is absolutely required for the downstream reporting system to understand the output. "
            "If instructed to read a file, ensure you use the exact path provided in the system instructions."
        )
        
        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(chat_history)
        
        if current_error_context:
            messages.append({
                "role": "user", 
                "content": f"Previous code failed with this error:\n{current_error_context}\nPlease fix it."
            })
        
        try:
            response = ollama.chat(model=MODEL_NAME, messages=messages)
            clean_code = response['message']['content'].strip().replace("```python", "").replace("```", "").strip()
            
            result = run_code_safely(clean_code, mount_dir=quarantine_dir)
            
            if any(err in result for err in ["Security Constraint Violated", "Error:", "SyntaxError", "Exception", "Traceback"]):
                logger.warning(f"Execution failed: {result}")
                current_error_context = result
            else:
                logger.info("Code executed successfully.")
                return result

        except Exception as e:
            logger.error(f"Fatal agent error: {str(e)}")
            break

    return "Task failed within security constraints."