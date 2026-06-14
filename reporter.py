import ollama
import logging

logger = logging.getLogger("AgenticSandbox")

def synthesize(task, raw_output=None, used_code=False):
    """
    Takes the raw execution output and the original user task, 
    then uses the LLM to generate a natural, human-readable response.
    """
    logger.info("Reporter Agent synthesizing final response...")
    
    if used_code:
        # Instruction for tasks that required code execution
        system_instruction = (
            "You are a Technical Reporter Agent. Your job is to answer the user's query based STRICTLY "
            "on the provided raw execution output from a secure sandbox. "
            "Do not make up numbers or guess. Explain the output clearly and naturally in the user's language."
        )
        prompt = f"{system_instruction}\n\nUser Query: {task}\nRaw Sandbox Output:\n{raw_output}\n\nProvide the final answer:"
    else:
        # Instruction for general text questions
        system_instruction = (
            "You are a helpful AI assistant. Answer the user's general question clearly, accurately, and concisely."
        )
        prompt = f"{system_instruction}\n\nUser Query: {task}\n\nProvide the answer:"
        
    try:
        response = ollama.generate(model='llama3.1', prompt=prompt)
        return response['response'].strip()
    except Exception as e:
        logger.error(f"Reporter error: {str(e)}")
        return "System error while generating the final report."