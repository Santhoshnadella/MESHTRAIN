import time

class MetricsRegistry:
    """Mock Prometheus-style metrics registry for MeshTrain (V15)."""
    
    def __init__(self):
        self.counters = {}
        self.histograms = {}
        
    def inc_counter(self, name: str, value: int = 1):
        self.counters[name] = self.counters.get(name, 0) + value
        
    def observe(self, name: str, value: float):
        if name not in self.histograms:
            self.histograms[name] = []
        self.histograms[name].append(value)
        
    def get_metrics(self):
        """Returns the metrics in Prometheus exposition format."""
        lines = []
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
            
        for name, values in self.histograms.items():
            lines.append(f"# TYPE {name} summary")
            if values:
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
                
        return "\n".join(lines)

metrics = MetricsRegistry()

class ReputationManager:
    """Tracks performance and reliability of peers on the network."""
    
    def __init__(self):
        self.scores = {}
        
    def add_score(self, peer_id: str, points: float):
        self.scores[peer_id] = self.scores.get(peer_id, 100.0) + points
        
    def penalize(self, peer_id: str, points: float):
        self.scores[peer_id] = self.scores.get(peer_id, 100.0) - points
        
    def get_score(self, peer_id: str) -> float:
        return self.scores.get(peer_id, 100.0)

reputation = ReputationManager()
