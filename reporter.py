import ollama
import logging

logger = logging.getLogger("AgenticSandbox")

def synthesize(chat_history, raw_output=None, used_code=False):
    """Generates a natural language response based on conversation history and execution results."""
    logger.info("Reporter Agent synthesizing final response...")
    
    if used_code:
        # Instruction for explaining technical logs
        system_instruction = (
            "You are a Technical Reporter Agent. Answer the user's latest query based STRICTLY "
            "on the provided raw execution output from a secure sandbox. "
            "Do not make up numbers or guess. Explain the output clearly and naturally.\n\n"
            f"[RAW SANDBOX OUTPUT]:\n{raw_output}\n"
        )
    else:
        # Instruction for general assistance
        system_instruction = (
            "You are a helpful AI assistant. Answer the user's general question clearly, accurately, and concisely."
        )
        
    messages = [{"role": "system", "content": system_instruction}]
    messages.extend(chat_history)
        
    try:
        response = ollama.chat(model='llama3.1', messages=messages)
        return response['message']['content'].strip()
    except Exception as e:
        logger.error(f"Reporter error: {str(e)}")
        return "System error while generating the final report."