from meshtrain.scheduler.planner import JobPlanner
from meshtrain.network.peer import Peer
from meshtrain.node.agent import MeshNode
from meshtrain.verification.consensus import ConsensusEngine
import asyncio

class InferenceRouter:
    """Routes an inference job to the optimal peer (MeshServe)."""
    
    def __init__(self, peer: Peer):
        self.peer = peer
        self.planner = JobPlanner(self.peer.peer_id)
        self.local_node = MeshNode()
        self.consensus = ConsensusEngine()
        
    async def run_inference(self, model: str, prompt: str, modality: str = "text", required_vram_gb: float = 2.0, verify: bool = True):
        """
        Determines where to run the inference based on available peers, VRAM, and modality.
        """
        if modality == "image":
            required_vram_gb = max(required_vram_gb, 8.0) # Images require more VRAM
            
        print(f"Routing {modality} inference request for {model} (Requires ~{required_vram_gb}GB VRAM)")
        
        target_peer_ids = self.planner.plan_inference_job(
            self.peer.peer_capabilities, 
            model_vram_requirement=required_vram_gb,
            num_peers=2 if verify else 1
        )
        
        if not target_peer_ids:
            print("Error: No peers (including local) have enough VRAM for this model.")
            return None
            
        # Convert to list if it's a single string for backward compatibility with older planner
        if isinstance(target_peer_ids, str):
            target_peer_ids = [target_peer_ids]
            
        if len(target_peer_ids) < 2 and verify:
            print("Warning: Verification enabled, but only 1 capable peer found. Falling back to single execution.")
            verify = False
            
        if not verify or len(target_peer_ids) == 1:
            # Standard single execution
            target_peer_id = target_peer_ids[0]
            if target_peer_id == self.peer.peer_id:
                print("Planner decision: Executing LOCALLY.")
                if modality == "image":
                    result = self.local_node.generate_image(prompt, model)
                    return result
                else:
                    result = self.local_node.infer(model, prompt)
                    return result
            else:
                print(f"Planner decision: Forwarding to remote peer {target_peer_id}.")
                await self.peer.send_inference_request(target_peer_id, model, prompt, modality)
                return {"status": "forwarded", "target": target_peer_id}
                
        else:
            # V8 Proof of Compute: Consensus Verification
            print(f"Consensus Verification (V8): Forwarding to {target_peer_ids[0]} AND {target_peer_ids[1]}.")
            
            # Create futures to wait for both responses
            await self.peer.send_inference_request(target_peer_ids[0], model, prompt, modality)
            await self.peer.send_inference_request(target_peer_ids[1], model, prompt, modality)
            
            return {"status": "forwarded_verify", "targets": target_peer_ids}
