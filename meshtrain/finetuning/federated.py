import os
import glob

class FederatedAverager:
    """
    V13: Handles true Federated Learning by mathematically averaging 
    multiple LoRA adapter weight files (FedAvg).
    """
    
    def __init__(self):
        try:
            self.torch = __import__('torch')
        except ImportError:
            self.torch = None
            
    def average_weights(self, adapter_dir: str = ".meshtrain/lora_received") -> str:
        """
        Loads all adapter_*.bin files in the directory, averages their 
        state dicts, and saves a master_adapter.bin.
        """
        if not self.torch:
            print("Warning: torch not installed. Cannot perform FedAvg.")
            return None
            
        adapter_files = glob.glob(os.path.join(adapter_dir, "adapter_*.bin"))
        if not adapter_files:
            print("No adapter files found for federated averaging.")
            return None
            
        print(f"Found {len(adapter_files)} peers' weights for Federated Averaging.")
        
        # Load all state dicts
        state_dicts = []
        for file in adapter_files:
            try:
                state_dicts.append(self.torch.load(file, map_location="cpu"))
            except Exception as e:
                print(f"Error loading {file}: {e}")
                
        if not state_dicts:
            return None
            
        # FedAvg Algorithm
        print("Performing FedAvg calculation...")
        avg_state_dict = {}
        for key in state_dicts[0].keys():
            # Sum the tensors across all state dicts
            avg_state_dict[key] = sum(sd[key] for sd in state_dicts) / len(state_dicts)
            
        # Save master adapter
        master_path = os.path.join(adapter_dir, "master_adapter.bin")
        self.torch.save(avg_state_dict, master_path)
        print(f"Federated Averaging complete! Master weights saved to {master_path}")
        
        return master_path
