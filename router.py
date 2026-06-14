import ollama
import logging
from code_agent import solve_with_retry
from reporter import synthesize

logger = logging.getLogger("AgenticSandbox")

def orchestrator(chat_history):
    """Determines the execution path based on the latest user request."""
    
    # Isolate the latest task for intent classification
    latest_task = chat_history[-1]['content']
    logger.info(f"Orchestrator analyzing new task: {latest_task}")
    
    # Binary prompt for routing decisions
    router_prompt = (
        "You are an AI router. Read the user's task and determine if it requires "
        "writing and executing Python code to calculate math, process data, or perform an action. "
        "Reply EXACTLY with the word 'CODE' if programming is needed. "
        "Reply EXACTLY with the word 'TEXT' if it is a general question, definition, or translation.\n\n"
        f"Task: {latest_task}"
    )
    
    try:
        response = ollama.generate(model='llama3.1', prompt=router_prompt)
        decision = response['response'].strip().upper().replace(".", "")
        
        logger.info(f"Orchestrator Decision: {decision}")
        
        if "CODE" in decision:
            logger.info("Routing: Task -> Code -> Broker -> Reporter")
            raw_execution_output = solve_with_retry(chat_history)
            return synthesize(chat_history, raw_output=raw_execution_output, used_code=True)
            
        else:
            logger.info("Routing: Task -> Reporter (Direct Text)")
            return synthesize(chat_history, raw_output=None, used_code=False)
            
    except Exception as e:
        logger.error(f"Router error: {str(e)}")
        return "System failure at the routing stage."