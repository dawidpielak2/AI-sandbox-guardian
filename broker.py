import docker
import requests

client = docker.from_env()

def run_code_safely(user_code, timeout_seconds=5):
    """Executes untrusted Python code inside an isolated Docker container with strict time limits."""
    print(f"[LOG] Launching execution in a secured sandbox...")
    try:
        # lunching container in the background 
        container = client.containers.run(
            image="ai-sandbox-image",
            command=[user_code],
            network_disabled=True,
            mem_limit="64m",
            detach=True
        )
        
        try:
            container.wait(timeout=timeout_seconds)
            output = container.logs().decode('utf-8').strip()
            return output
        except requests.exceptions.ReadTimeout:
            # DOS protection
            container.kill()
            return "Security Constraint Violated: Execution Timeout (DoS Prevention)"
        finally:
            container.remove(force=True)
            
    except Exception as e:
             return f"Security Constraint Violated: {str(e)}"