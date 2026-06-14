import ollama
import logging
from broker import run_code_safely

logger = logging.getLogger("AgenticSandbox")

def solve_with_retry(chat_history, max_retries=3):
    """Generates executable code using conversation context, runs it, and returns raw output."""
    current_error_context = ""
    
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} started.")
        
        # Core instruction enforcing executable code constraints
        system_instruction = (
            "You are an Expert Python Developer. Write raw Python code to solve the task. "
            "Return ONLY executable code. No explanations. No markdown formatting blocks. "
            "You MUST print the final result using print() so it can be captured by standard output."
        )
        
        # Construct the message payload
        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(chat_history)
        
        # Inject error logs for the self-healing process
        if current_error_context:
            messages.append({
                "role": "user", 
                "content": f"Previous code execution failed with this error:\n{current_error_context}\nPlease fix the code."
            })
        
        try:
            response = ollama.chat(model='llama3.1', messages=messages)
            clean_code = response['message']['content'].strip().replace("```python", "").replace("```", "").strip()
            
            result = run_code_safely(clean_code)
            
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