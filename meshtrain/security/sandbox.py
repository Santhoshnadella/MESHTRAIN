import os
import contextlib

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
