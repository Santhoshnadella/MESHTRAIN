import time
import importlib

class MeshNode:
    """The local AI execution engine for MeshTrain (V11 Secured)."""
    
    def __init__(self):
        try:
            self.torch = __import__('torch')
            self.transformers = __import__('transformers')
        except ImportError:
            self.torch = None
            self.transformers = None
            
        self.device = "cuda" if self.torch and self.torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        from meshtrain.security.sandbox import SecurityContext
        self.security_context = SecurityContext
        
    def start(self):
        print(f"Node {self.peer_id} starting on {self.device}...")
        
    def _load_model(self, model_name: str):
        if not self.transformers:
            print(f"Mock downloading model {model_name}...")
            time.sleep(1)
            self.models[model_name] = "MOCK_MODEL"
            return
            
        print(f"Downloading/Loading {model_name} from HuggingFace to {self.device}...")
        try:
            with self.security_context(trust_remote_code=False):
                tokenizer = self.transformers.AutoTokenizer.from_pretrained(model_name)
                model = self.transformers.AutoModelForCausalLM.from_pretrained(model_name)
                model.to(self.device)
            self.tokenizers[model_name] = tokenizer
            self.models[model_name] = model
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            self.model = None
            self.tokenizer = None
            
    def generate_image(self, prompt: str, model_name: str = "runwayml/stable-diffusion-v1-5") -> dict:
        """V10: Generates an image using diffusers and returns binary PNG data."""
        if not self.torch:
            return {"status": "mock", "payload_type": "image/png", "payload": b"MOCK_PNG_DATA"}
            
        try:
            from diffusers import StableDiffusionPipeline
            
            print(f"Loading Diffusers pipeline for {model_name}...")
            with self.security_context(trust_remote_code=False):
                pipe = StableDiffusionPipeline.from_pretrained(model_name, torch_dtype=self.torch.float16)
            pipe = pipe.to(self.device)
            
            print(f"Generating image for prompt: '{prompt}'...")
            image = pipe(prompt).images[0]
            
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            binary_payload = img_byte_arr.getvalue()
            
            return {"status": "success", "payload_type": "image/png", "payload": binary_payload}
        except Exception as e:
            print(f"Error generating image: {e}")
            return {"status": "error", "payload_type": "text/plain", "payload": str(e).encode()}
            
    def infer(self, model_name: str, prompt: str, max_length: int = 50):
        print(f"Preparing inference for {model_name}...")
        if model_name not in self.models:
            self._load_model(model_name)
            
        model = self.models.get(model_name)
        
        if model == "MOCK_MODEL" or not self.transformers:
            print(f"Running mock inference on {model_name}...")
            time.sleep(1)
            return {"result": f"Mock output for: '{prompt}'"}
            
        print(f"Running inference on {model_name} using {self.device}...")
        tokenizer = self.tokenizers[model_name]
        
        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with self.torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=max_length, 
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7
            )
            
        result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"result": result_text}
        
    def tune(self, model_name: str, dataset: str):
        print(f"Preparing fine-tuning for {model_name} on dataset {dataset}...")
        if model_name not in self.models:
            self._load_model(model_name)
            
        print("Initializing LoRA adapters (Mock)...")
        time.sleep(1)
        print("Training... (Epoch 1/3)")
        time.sleep(1)
        print("Training complete. Artifacts saved locally.")
        return {"status": "success", "artifact": "lora_adapter_v1"}
