from meshtrain.scheduler.scoring import PeerScorer
from meshtrain.capability.gpu import HardwareDetector
from typing import Dict, Any, Optional

class JobPlanner:
    """Decides where a workload should execute (Local vs Remote)."""
    
    def __init__(self, local_peer_id: str):
        self.local_peer_id = local_peer_id
        self.local_hw = HardwareDetector().detect()
        
    def plan_inference_job(self, connected_peers: Dict[str, Dict[str, Any]], model_vram_requirement: float) -> Optional[str]:
        """
        Determines the best peer_id to execute an inference job.
        Returns the local_peer_id if the local machine is best/sufficient,
        otherwise returns the remote peer_id. Returns None if no peer can handle it.
        """
        
        # Include ourselves in the candidate pool
        all_candidates = connected_peers.copy()
        all_candidates[self.local_peer_id] = {"hardware": self.local_hw}
        
        ranked_peers = PeerScorer.score_peers(all_candidates, required_vram_gb=model_vram_requirement)
        
        if not ranked_peers:
            return None # No one can handle this job
            
        # For MVP: just take the top ranked peer
        best_peer = ranked_peers[0]
        
        # Tie-breaker / Local Preference: If local node is capable enough, just run it locally
        if self.local_peer_id in ranked_peers:
            local_vram = self.local_hw.get("vram_gb", 0)
            if local_vram >= model_vram_requirement:
                # We have enough VRAM locally, save network overhead
                return self.local_peer_id
                
        return best_peer
