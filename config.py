MODEL_NAME = "llama3.1"

# Chat Memory Constraints
MAX_HISTORY_LENGTH = 10
MAX_TEXT_READ_SIZE = 20480  # 20 KB limit for direct text reading without the Code Agent

# Docker Sandbox Constraints
DOCKER_IMAGE_NAME = "ai-sandbox-image"
DOCKER_MEM_LIMIT = "64m"
EXECUTION_TIMEOUT_SECONDS = 5