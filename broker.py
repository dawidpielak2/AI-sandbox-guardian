import docker
import requests
from config import DOCKER_IMAGE_NAME, DOCKER_MEM_LIMIT, EXECUTION_TIMEOUT_SECONDS

client = docker.from_env()

def run_code_safely(user_code, mount_dir=None):
    """Executes code in a secure container using limits from the config file."""
    print(f"[LOG] Launching execution in a secured sandbox...")
    
    volumes_config = None
    if mount_dir:
        volumes_config = {
            mount_dir: {
                'bind': '/mnt/sandbox_data',
                'mode': 'ro'
            }
        }
        
    try:
        container = client.containers.run(
            image=DOCKER_IMAGE_NAME,
            command=[user_code],
            network_disabled=True,
            mem_limit=DOCKER_MEM_LIMIT,
            volumes=volumes_config,
            detach=True
        )
        
        try:
            # Uses the timeout from config.py
            container.wait(timeout=EXECUTION_TIMEOUT_SECONDS)
            output = container.logs().decode('utf-8').strip()
            return output
        except requests.exceptions.ReadTimeout:
            container.kill()
            return "Security Constraint Violated: Execution Timeout (DoS Prevention)"
        finally:
            container.remove(force=True)
            
    except Exception as e:
        return f"Security Constraint Violated: {str(e)}"