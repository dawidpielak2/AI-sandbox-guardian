import ollama
import logging
from code_agent import solve_with_retry
from reporter import synthesize

logger = logging.getLogger("AgenticSandbox")

def orchestrator(task):
    """Determines the path: Code Generation -> Synthesizer OR Direct to Synthesizer."""
    logger.info(f"Orchestrator analyzing task: {task}")
    
    # Restrictive binary prompt (Only the word CODE or TEXT)
    router_prompt = (
        "You are an AI router. Read the user's task and determine if it requires "
        "writing and executing Python code to calculate math, process data, or perform an action. "
        "Reply EXACTLY with the word 'CODE' if programming is needed. "
        "Reply EXACTLY with the word 'TEXT' if it is a general question, definition, or translation.\n\n"
        f"Task: {task}"
    )
    
    try:
        response = ollama.generate(model='llama3.1', prompt=router_prompt)
        decision = response['response'].strip().upper().replace(".", "")
        
        logger.info(f"Orchestrator Decision: {decision}")
        
        if "CODE" in decision:
            logger.info("Routing: Task -> Code Agent -> Broker -> Reporter")
            # 1. Get raw output from the executed script
            raw_execution_output = solve_with_retry(task)
            # 2. Pass raw output to the Reporter for a readable explanation
            return synthesize(task, raw_output=raw_execution_output, used_code=True)
            
        else:
            logger.info("Routing: Task -> Reporter (Direct Text)")
            # 1. Question doesn't require code, pass directly to Reporter
            return synthesize(task, raw_output=None, used_code=False)
            
    except Exception as e:
        logger.error(f"Router error: {str(e)}")
        return "System failure at the routing stage."