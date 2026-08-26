import hashlib

class ConsensusEngine:
    """Provides Proof of Compute by verifying cryptographic hashes of multi-party inference results (V12)."""
    
    def __init__(self):
        pass
        
    def _hash_result(self, result: str) -> str:
        """Returns the SHA-256 hash of the result string."""
        return hashlib.sha256(result.encode('utf-8')).hexdigest()
        
    def verify(self, results: list) -> dict:
        """
        Takes a list of result strings from multiple peers for the same job.
        Verifies consensus by checking if the majority of hashes match.
        Assumes the job was run with a deterministic seed.
        """
        if not results or len(results) < 2:
            return {"verified": False, "consensus_hash": None, "reason": "Not enough results for consensus"}
            
        # Tally hashes
        hash_tally = {}
        for res in results:
            h = self._hash_result(res)
            hash_tally[h] = hash_tally.get(h, 0) + 1
            
        # Find the most common hash
        best_hash = max(hash_tally, key=hash_tally.get)
        max_votes = hash_tally[best_hash]
        
        # We need a strict majority
        is_verified = max_votes > (len(results) / 2)
        
        return {
            "verified": is_verified,
            "consensus_hash": best_hash,
            "votes": max_votes,
            "total_peers": len(results)
        }
