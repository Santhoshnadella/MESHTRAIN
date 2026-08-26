from typing import List, Dict, Any

class PeerScorer:
    """Ranks available peers based on their hardware capabilities."""
    
    @staticmethod
    def score_peers(peers_info: Dict[str, Dict[str, Any]], required_vram_gb: float = 0.0) -> List[str]:
        """
        Takes a dictionary of peer_id -> hardware_specs and returns a sorted list of peer_ids
        (best to worst). Filters out peers that do not meet the minimum VRAM requirement.
        """
        valid_peers = []
        
        for peer_id, capabilities in peers_info.items():
            # For this MVP, we assume the hardware dictionary matches our Protobuf schema
            hw = capabilities.get("hardware", {})
            vram = hw.get("vram_gb", 0.0)
            compute = hw.get("compute_score", 0)
            
            if vram >= required_vram_gb:
                # Basic scoring strategy: prioritize highest VRAM, then compute score
                score = (vram * 100) + compute
                valid_peers.append((peer_id, score))
                
        # Sort by score descending
        valid_peers.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in valid_peers]
