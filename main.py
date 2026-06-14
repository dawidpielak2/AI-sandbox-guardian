import logging
import sys
from router import orchestrator
from config import MAX_HISTORY_LENGTH
from file_manager import QUARANTINE_DIR, process_uploaded_file

# Global logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("security_audit.log")]
)

if __name__ == "__main__":
    print("\n=== AI Orchestrator Guardian ===")
    print("Type 'exit' or 'quit' to end the session.")
    print("Use '/load <absolute_path>' to mount a text file into the sandbox.\n")

    chat_history = []
    current_file = None

    while True:
        try:
            user_input = input("[You]: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nShutting down Guardian. Goodbye!")
                break
            
            if not user_input:
                continue
                
            # Handle the /load command using the file_manager
            if user_input.startswith("/load "):
                filepath = user_input[6:].strip()
                
                file_data = process_uploaded_file(filepath)
                
                if file_data["error"]:
                    print(f"[Guardian Error]: {file_data['error']}")
                    continue
                    
                # Store the current file details
                current_file = {
                    'name': file_data['name'], 
                    'path': file_data['path'], 
                    'size': file_data['size']
                }
                
                system_msg = (
                    f"System Note: The file '{file_data['name']}' is securely mounted at '/mnt/sandbox_data/{file_data['name']}'. "
                    f"Size category: {file_data['size_label']}. "
                    f"Content preview:\n{file_data['preview']}"
                )
                chat_history.append({"role": "system", "content": system_msg})
                print(f"[Guardian]: File '{file_data['name']}' safely loaded. Status: {file_data['size_label']}.")
                continue

            chat_history.append({"role": "user", "content": user_input})
            
            # Keep the history within the configured limit
            if len(chat_history) > MAX_HISTORY_LENGTH:
                chat_history = chat_history[-MAX_HISTORY_LENGTH:]

            print("--- Processing ---")
            
            final_output = orchestrator(chat_history, QUARANTINE_DIR, current_file)
            
            print(f"\n[FINAL REPORT]:\n{final_output}\n")
            print("-" * 50)
            
            chat_history.append({"role": "assistant", "content": final_output})

        except KeyboardInterrupt:
            print("\nShutting down Guardian. Goodbye!")
            break