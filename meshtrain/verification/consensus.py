import difflib

class ConsensusEngine:
    """Provides Proof of Compute by verifying multiple inference results (V8)."""
    
    def __init__(self, similarity_threshold: float = 0.80):
        self.similarity_threshold = similarity_threshold
        
    def verify(self, result_a: str, result_b: str) -> dict:
        """
        Compares two text generations. Returns a dict with 'verified' boolean
        and the similarity score.
        """
        if not result_a or not result_b:
            return {"verified": False, "score": 0.0, "reason": "Missing result"}
            
        # Calculate structural similarity using SequenceMatcher
        # LLMs generate slightly different text, but structure/semantics should be similar
        matcher = difflib.SequenceMatcher(None, result_a, result_b)
        score = matcher.ratio()
        
        is_verified = score >= self.similarity_threshold
        
        return {
            "verified": is_verified,
            "score": score,
            "result_a": result_a,
            "result_b": result_b
        }
