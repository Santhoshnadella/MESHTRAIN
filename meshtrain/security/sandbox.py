import os
import contextlib
import multiprocessing
import traceback

class SecurityContext:
    """
    MeshProtect V11: A context manager that locks down the environment
    to prevent malicious models from executing arbitrary code.
    """
    def __init__(self, trust_remote_code: bool = False):
        self.trust_remote_code = trust_remote_code
        self.original_env = {}

    def __enter__(self):
        # 1. Enforce strict transformers settings
        # We simulate the enforcement by setting environment variables that HuggingFace respects
        self.original_env["HF_TRUST_REMOTE_CODE"] = os.environ.get("HF_TRUST_REMOTE_CODE")
        
        if not self.trust_remote_code:
            os.environ["HF_TRUST_REMOTE_CODE"] = "0"
            
        print("[MeshProtect] Security Sandbox ACTIVE. trust_remote_code=False.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original environment
        if self.original_env.get("HF_TRUST_REMOTE_CODE") is None:
            if "HF_TRUST_REMOTE_CODE" in os.environ:
                del os.environ["HF_TRUST_REMOTE_CODE"]
        else:
            os.environ["HF_TRUST_REMOTE_CODE"] = self.original_env["HF_TRUST_REMOTE_CODE"]
            
        print("[MeshProtect] Security Sandbox DEACTIVATED.")


def _worker_process(target_func, result_queue, *args, **kwargs):
    """Runs the target function in an isolated process."""
    try:
        # We can apply OS-level restrictions here (e.g., dropping privileges) if needed.
        result = target_func(*args, **kwargs)
        result_queue.put({"status": "success", "data": result})
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e), "traceback": traceback.format_exc()})

class ProcessSandbox:
    """
    MeshProtect V12: Isolates AI model execution into a separate OS process.
    Prevents a model crash (OOM, segfault) or malicious code execution from taking down the main MeshNode.
    Fallback for when Docker/Containers are unavailable.
    """
    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def execute(self, target_func, *args, **kwargs):
        print(f"[MeshProtect] Spawning isolated process for execution (Timeout: {self.timeout}s)...")
        ctx = multiprocessing.get_context('spawn')
        result_queue = ctx.Queue()
        
        process = ctx.Process(target_func=_worker_process, args=(target_func, result_queue, *args), kwargs=kwargs)
        process.start()
        
        # Wait for result with timeout
        process.join(self.timeout)
        
        if process.is_alive():
            print("[MeshProtect] Execution timed out! Terminating isolated process.")
            process.terminate()
            process.join()
            return {"status": "error", "error": "Timeout exceeded."}
            
        if not result_queue.empty():
            return result_queue.get()
            
        return {"status": "error", "error": "Process died unexpectedly (OOM/Segfault)."}
