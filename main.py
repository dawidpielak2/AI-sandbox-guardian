import logging
import sys
from router import orchestrator

# Global logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("security_audit.log")]
)

# Limit for conversation history to prevent context window overflow
MAX_HISTORY_LENGTH = 10

if __name__ == "__main__":
    print("\n=== AI Orchestrator Guardian (Interactive Chat Mode) ===")
    print("Type 'exit' or 'quit' or press 'Ctrl + C' to end the session.\n")

    # Short-term memory for the AI model
    chat_history = []

    while True:
        try:
            user_input = input("[You]: ").strip()
            
            # Exit mechanism
            if user_input.lower() in ['exit', 'quit']:
                print("\nShutting down Guardian. Goodbye!")
                break
            
            if not user_input:
                continue
                
            # Append user message to history
            chat_history.append({"role": "user", "content": user_input})
            
            # Enforce sliding window to manage memory usage
            if len(chat_history) > MAX_HISTORY_LENGTH:
                chat_history = chat_history[-MAX_HISTORY_LENGTH:]

            print("--- Thinking... ---")
            
            # Pass the conversation history to the routing layer
            final_output = orchestrator(chat_history)
            
            print(f"\n[Guardian]:\n{final_output}\n")
            print("-" * 50)
            
            # Append AI response to history for context in future queries
            chat_history.append({"role": "assistant", "content": final_output})

        except KeyboardInterrupt:
            print("\nShutting down Guardian. Goodbye!")
            sys.exit(0)