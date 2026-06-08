import docker
import requests 

client = docker.from_env()

def run_code_safely(user_code, timeout_seconds=5):
    """
    Executes code with strict time and resource limits.
    """
    print(f"[LOG] Testing security constraints...")
    try:
        execution_result = client.containers.run(
            image="ai-sandbox-image",
            command=[user_code],
            network_disabled=True,
            mem_limit="64m",
            remove=True,
            stdout=True,
            stderr=True,
            timeout=timeout_seconds 
        )
        return execution_result.decode('utf-8').strip()
    
    except Exception as e:
        return f"Security Constraint Violated: {str(e)}"
