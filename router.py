import ollama
import logging
from code_agent import solve_with_retry
from reporter import synthesize
from config import MODEL_NAME

logger = logging.getLogger("AgenticSandbox")

def orchestrator(chat_history, quarantine_dir=None, current_file=None):
    """Determines the execution path based on intent and file size constraints."""
    
    latest_task = chat_history[-1]['content']
    logger.info(f"Orchestrator analyzing new task: {latest_task}")
    
    router_prompt = (
        "You are an AI router. Read the user's task and determine the correct execution path.\n\n"
        "Reply EXACTLY with the word 'CODE' if ANY of these conditions are met:\n"
        "- The user explicitly asks to write a script, program, or code.\n"
        "- The user asks to calculate math or extract specific data.\n"
        "- The user wants to analyze a file AND the file size category is LARGE.\n\n"
        "Reply EXACTLY with the word 'TEXT' if ALL of these conditions are met:\n"
        "- The task is a general question, text summarization, or translation.\n"
        "- The file size category is NOT LARGE.\n\n"
        f"Task: {latest_task}"
    )
    
    try:
        response = ollama.generate(model=MODEL_NAME, prompt=router_prompt)
        decision = response['response'].strip().upper().replace(".", "")
        
        logger.info(f"Orchestrator Decision: {decision}")
        
        if "CODE" in decision:
            logger.info("Routing: Task -> Code Agent -> Broker -> Reporter")
            raw_execution_output = solve_with_retry(chat_history, quarantine_dir)
            return synthesize(chat_history, raw_output=raw_execution_output, used_code=True, current_file=current_file)
            
        else:
            logger.info("Routing: Task -> Reporter (Direct Text)")
            return synthesize(chat_history, raw_output=None, used_code=False, current_file=current_file)
            
    except Exception as e:
        logger.error(f"Router error: {str(e)}")
        return "System failure at the routing stage."