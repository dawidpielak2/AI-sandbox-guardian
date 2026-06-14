import ollama
import logging
from config import MODEL_NAME, MAX_TEXT_READ_SIZE

logger = logging.getLogger("AgenticSandbox")

def synthesize(chat_history, raw_output=None, used_code=False, current_file=None):
    """Generates the final response and reads small files directly if needed."""
    logger.info("Reporter Agent synthesizing final response...")
    
    if used_code:
        system_instruction = (
            "You are a Technical Reporter Agent. "
            "The user's task HAS ALREADY BEEN SOLVED and EXECUTED by a separate background code engine. "
            "Your ONLY responsibility is to present the final results to the user in a clear and natural way. "
            "CRITICAL RULES:\n"
            "1. DO NOT write, generate, or display any programming code. The code was already executed.\n"
            "2. Base your answer STRICTLY on the [RAW SANDBOX OUTPUT] provided below.\n"
            "3. If the user originally asked to 'write a script', ignore that command. Just provide the results of the execution.\n\n"
            f"[RAW SANDBOX OUTPUT]:\n{raw_output}\n"
        )
    else:
        system_instruction = (
            "You are a helpful AI assistant. Answer the user's general question clearly, accurately, and concisely."
        )
        
        if current_file and current_file['size'] <= MAX_TEXT_READ_SIZE:
            try:
                with open(current_file['path'], 'r', encoding='utf-8') as f:
                    full_content = f.read()
                
                logger.info(f"Injecting full content of {current_file['name']} into Reporter's prompt.")
                system_instruction += (
                    f"\n\n[FULL CONTENT OF UPLOADED FILE '{current_file['name']}']:\n{full_content}\n"
                    "Use the text above to fulfill the user's request."
                )
            except Exception as e:
                logger.error(f"Failed to load file content for Reporter: {str(e)}")
        
    messages = [{"role": "system", "content": system_instruction}]
    messages.extend(chat_history)
        
    try:
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        return response['message']['content'].strip()
    except Exception as e:
        logger.error(f"Reporter error: {str(e)}")
        return "System error while generating the final report."