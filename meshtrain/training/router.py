from meshtrain.scheduler.planner import JobPlanner
from meshtrain.network.peer import Peer
from meshtrain.finetuning.federated import FederatedAverager
import asyncio
from meshtrain.finetuning.lora import LoRATuner
from meshtrain.storage.content_store import ContentStore
import os
import asyncio

class TrainingRouter:
    """Routes a fine-tuning job to the optimal peer (MeshTune)."""
    
    def __init__(self, peer: Peer):
        self.peer = peer
        self.planner = JobPlanner(self.peer.peer_id)
        self.local_tuner = LoRATuner()
        self.store = ContentStore()
        
    async def run_training(self, model: str, dataset_path: str, required_vram_gb: float = 12.0):
    async def run_training(self, model: str, dataset_path: str, num_peers: int = 1):
        print(f"Routing training request for {model} to {num_peers} peer(s).")
        
        # Requires at least 12GB VRAM for LoRA
        target_peer_ids = self.planner.plan_training_job(
            self.peer.peer_capabilities, 
            model_vram_requirement=12.0,
            num_peers=num_peers
        )
        
        if not target_peer_ids:
            print("Error: No peers (including local) have enough VRAM for training.")
            return None
            
        # Convert to list
        if isinstance(target_peer_ids, str):
            target_peer_ids = [target_peer_ids]
            
        # 1. Chunk dataset into ContentStore
        print(f"Chunking {dataset_path} into P2P ContentStore...")
        manifest_hash = self.store.add_file(dataset_path)
        print(f"Dataset manifest hash: {manifest_hash}")
            
        if len(target_peer_ids) == 1 and target_peer_ids[0] == self.peer.peer_id:
            print("Planner decision: Executing LOCALLY.")
            adapter_path = self.peer.lora_tuner.train(model, dataset_path)
            return {"status": "success", "adapter_size": 1024}
        else:
            print(f"Planner decision: Forwarding to remote peers: {target_peer_ids}")
            
            # Send to all selected peers for Federated Learning
            for target_id in target_peer_ids:
                if target_id == self.peer.peer_id: continue
                await self.peer.send_training_request(target_id, model, manifest_hash)
            
            # In a real async runtime, we would await all results. We simulate it here.
            # When results arrive, peer.py will save them.
            if len(target_peer_ids) > 1:
                print("[Federated Learning] Awaiting multiple results for FedAvg...")
                return {"status": "forwarded_federated", "targets": target_peer_ids}
                
            return {"status": "forwarded", "target": target_peer_ids[0]}
