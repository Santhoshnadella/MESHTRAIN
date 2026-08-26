import time
import os
import importlib

class LoRATuner:
    """Handles Parameter-Efficient Fine-Tuning (V6)."""
    
    def __init__(self):
        try:
            self.torch = importlib.import_module("torch")
            self.transformers = importlib.import_module("transformers")
            self.peft = importlib.import_module("peft")
            self.datasets = importlib.import_module("datasets")
        except ImportError:
            self.torch = None
            self.transformers = None
            self.peft = None
            self.datasets = None
            print("Warning: ML dependencies not installed. LoRA tuning will run in mock mode.")
            
        self.device = "cuda" if self.torch and self.torch.cuda.is_available() else "cpu"

    def tune(self, model_name: str, dataset_path: str) -> bytes:
        """
        Loads a base model, applies LoRA, trains on the local dataset_path,
        and returns the binary adapter weights.
        """
        if not self.peft:
            print(f"Mock training {model_name} on {dataset_path}...")
            time.sleep(2)
            return b"MOCK_LORA_WEIGHTS"
            
        print(f"Initializing LoRA training for {model_name} on {self.device}...")
        
        try:
            tokenizer = self.transformers.AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model = self.transformers.AutoModelForCausalLM.from_pretrained(
                model_name, 
                torch_dtype=self.torch.float16 if self.device == "cuda" else self.torch.float32
            )
            
            # 1. Setup LoRA Config
            peft_config = self.peft.LoraConfig(
                task_type=self.peft.TaskType.CAUSAL_LM,
                inference_mode=False,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1
            )
            
            # 2. Get PEFT Model
            peft_model = self.peft.get_peft_model(model, peft_config)
            peft_model.print_trainable_parameters()
            
            # 3. Load dataset
            dataset = self.datasets.load_dataset("json", data_files=dataset_path, split="train")
            
            def tokenize_function(examples):
                return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)
                
            tokenized_datasets = dataset.map(tokenize_function, batched=True)
            
            # 4. Train
            training_args = self.transformers.TrainingArguments(
                output_dir=".meshtrain/checkpoints",
                per_device_train_batch_size=1,
                gradient_accumulation_steps=4,
                max_steps=10, # Very small mock run for MVP
                learning_rate=2e-4,
                logging_steps=1,
            )
            
            trainer = self.transformers.Trainer(
                model=peft_model,
                args=training_args,
                train_dataset=tokenized_datasets,
            )
            
            print("Starting LoRA fine-tuning...")
            trainer.train()
            
            # 5. Extract weights
            output_dir = ".meshtrain/lora_out"
            peft_model.save_pretrained(output_dir)
            
            adapter_path = os.path.join(output_dir, "adapter_model.bin")
            # If safe_tensors is used, it might be adapter_model.safetensors
            if not os.path.exists(adapter_path):
                adapter_path = os.path.join(output_dir, "adapter_model.safetensors")
                
            with open(adapter_path, "rb") as f:
                adapter_weights = f.read()
                
            return adapter_weights
            
        except Exception as e:
            print(f"Error during training: {e}")
            return b"ERROR"
