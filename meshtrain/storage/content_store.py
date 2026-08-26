import hashlib
import os
import json
from typing import List, Dict

CHUNK_SIZE = 1024 * 1024 * 5 # 5 MB chunks

class ContentStore:
    """BitTorrent-style content-addressed storage (V4 scaffold)."""
    
    def __init__(self, base_dir=".meshtrain/store"):
        self.base_dir = base_dir
        os.makedirs(os.path.join(self.base_dir, "chunks"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "manifests"), exist_ok=True)
        
    def add_file(self, file_path: str) -> str:
        """Chunks a file and returns its manifest hash."""
        chunks = []
        
        with open(file_path, "rb") as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                
                chunk_hash = hashlib.sha256(data).hexdigest()
                chunk_path = os.path.join(self.base_dir, "chunks", chunk_hash)
                
                with open(chunk_path, "wb") as cf:
                    cf.write(data)
                    
                chunks.append(chunk_hash)
                
        manifest = {
            "filename": os.path.basename(file_path),
            "total_size": os.path.getsize(file_path),
            "chunk_size": CHUNK_SIZE,
            "chunks": chunks
        }
        
        manifest_data = json.dumps(manifest, sort_keys=True).encode()
        manifest_hash = hashlib.sha256(manifest_data).hexdigest()
        
        manifest_path = os.path.join(self.base_dir, "manifests", f"{manifest_hash}.json")
        with open(manifest_path, "wb") as mf:
            mf.write(manifest_data)
            
        return manifest_hash
        
    def replicate_chunk(self, chunk_hash: str, network_peer):
        """
        MeshDrive (V7): Instructs the network peer to push this chunk to 
        2 random peers on the DHT for decentralized persistence.
        """
        chunk_path = os.path.join(self.chunks_dir, chunk_hash)
        if not os.path.exists(chunk_path):
            return False
            
        # In the MVP, we just call the peer's pin method which handles the network request
        print(f"MeshDrive: Queuing {chunk_hash} for replication to DHT peers...")
        import asyncio
        # We don't await here to avoid blocking the chunking process, we fire and forget
        asyncio.create_task(network_peer.pin_chunk_to_dht(chunk_hash, chunk_path))
        return True
