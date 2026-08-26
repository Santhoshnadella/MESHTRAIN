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
            
    def average_weights(self, adapter_dir: str = ".meshtrain/lora_received", metadata: dict = None) -> str:
        """
        Loads all adapter_*.bin files in the directory, averages their 
        state dicts using a weighted average (if metadata provided), 
        and saves a master_adapter.bin.
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
        weights = [] # For weighted average based on samples processed
        
        for file in adapter_files:
            try:
                state_dicts.append(self.torch.load(file, map_location="cpu"))
                peer_id = os.path.basename(file).split('_')[1].split('.')[0]
                # Default weight is 1.0 if no metadata provided
                weight = metadata.get(peer_id, {}).get("samples_processed", 1.0) if metadata else 1.0
                weights.append(weight)
            except Exception as e:
                print(f"Error loading {file}: {e}")
                
        if not state_dicts:
            return None
            
        # FedAvg Algorithm (Robust Weighted Average)
        print("Performing Robust FedAvg calculation...")
        total_weight = sum(weights)
        avg_state_dict = {}
        for key in state_dicts[0].keys():
            # Weighted sum across all state dicts
            avg_state_dict[key] = sum(sd[key] * (w / total_weight) for sd, w in zip(state_dicts, weights))
            
        # Save master adapter
        master_path = os.path.join(adapter_dir, "master_adapter.bin")
        self.torch.save(avg_state_dict, master_path)
        print(f"Federated Averaging complete! Master weights saved to {master_path}")
        
        return master_path

    def save_checkpoint(self, state_dict: dict, round_num: int, checkpoint_dir: str = ".meshtrain/checkpoints"):
        """Saves a distributed training checkpoint to resume later."""
        if not self.torch: return
        os.makedirs(checkpoint_dir, exist_ok=True)
        path = os.path.join(checkpoint_dir, f"checkpoint_round_{round_num}.bin")
        self.torch.save(state_dict, path)
        print(f"[FedAvg] Checkpoint saved: {path}")
        
    def load_latest_checkpoint(self, checkpoint_dir: str = ".meshtrain/checkpoints"):
        """Loads the most recent checkpoint for state resume."""
        if not self.torch: return None, 0
        checkpoints = glob.glob(os.path.join(checkpoint_dir, "checkpoint_round_*.bin"))
        if not checkpoints:
            return None, 0
            
        # Sort by round number
        latest = max(checkpoints, key=lambda p: int(os.path.basename(p).split('_')[-1].split('.')[0]))
        round_num = int(os.path.basename(latest).split('_')[-1].split('.')[0])
        print(f"[FedAvg] Resuming from checkpoint: {latest}")
        return self.torch.load(latest, map_location="cpu"), round_num
