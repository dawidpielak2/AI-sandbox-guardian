import os
import shutil
import tempfile
import atexit
import logging
from config import MAX_TEXT_READ_SIZE

# Create the hidden quarantine folder when the module loads
QUARANTINE_DIR = tempfile.mkdtemp(prefix="ai_sandbox_data_")

def cleanup_quarantine():
    """Removes the quarantine directory and isolated files when the program stops."""
    if os.path.exists(QUARANTINE_DIR):
        shutil.rmtree(QUARANTINE_DIR)
        logging.info(f"Quarantine directory removed: {QUARANTINE_DIR}")

# Register the cleanup function to trigger on exit or crash
atexit.register(cleanup_quarantine)

def process_uploaded_file(filepath):
    """
    Validates, copies, and extracts metadata from the user's file.
    Returns a dictionary with file information or an error message.
    """
    if not os.path.isfile(filepath):
        return {"error": "Invalid file path."}
    
    if not filepath.endswith('.txt'):
        return {"error": "Only .txt files are supported."}

    filename = os.path.basename(filepath)
    safe_path = os.path.join(QUARANTINE_DIR, filename)
    
    # Copy the file to the quarantine folder
    shutil.copy2(filepath, safe_path)
    file_size = os.path.getsize(safe_path)
    
    # Check if the file is small enough for the model to read directly
    is_large = file_size > MAX_TEXT_READ_SIZE
    size_label = "LARGE (Requires CODE Agent to analyze)" if is_large else "SMALL (Reporter can read directly)"
    
    # Generate a preview of the text
    with open(safe_path, 'r', encoding='utf-8') as f:
        preview = f.read(500) + ("..." if is_large else "")
        
    return {
        "error": None,
        "name": filename,
        "path": safe_path,
        "size": file_size,
        "size_label": size_label,
        "preview": preview
    }