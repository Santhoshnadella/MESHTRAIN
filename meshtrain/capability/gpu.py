import importlib

class HardwareDetector:
    """Detects local hardware capabilities (V0)."""
    
    def __init__(self):
        self.torch = None
        try:
            self.torch = importlib.import_module("torch")
        except ImportError:
            pass
        
    def detect(self):
        if self.torch and self.torch.cuda.is_available():
            device_count = self.torch.cuda.device_count()
            gpu_name = self.torch.cuda.get_device_name(0)
            vram_bytes = self.torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram_bytes / (1024 ** 3)
            return {
                "gpu": gpu_name,
                "vram_gb": round(vram_gb, 2),
                "compute_score": 90, # Placeholder benchmark
                "backend": "CUDA",
                "device_count": device_count
            }
        
        # CPU Fallback
        return {
            "gpu": "CPU_ONLY",
            "vram_gb": 0,
            "compute_score": 10,
            "backend": "CPU",
            "device_count": 0
        }
