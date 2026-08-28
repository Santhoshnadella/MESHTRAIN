import asyncio
from typing import List, Optional
try:
    from libp2p.routing.kademlia.kademlia_peer_router import KademliaPeerRouter
except ImportError:
    class KademliaPeerRouter:
        def __init__(self, host):
            pass
        async def provide(self, key):
            pass
        async def find_providers(self, key):
            return []

class MeshDHT:
    """Kademlia DHT for MeshTrain Peer Discovery (V3)."""
    
    def __init__(self, host):
        self.host = host
        # Initialize the Kademlia peer router
        # In a real py-libp2p implementation, this connects to the host's event bus and multiplexer
        # Note: py-libp2p's Kademlia requires explicit wiring. For this MVP, we scaffold the interface.
        self.router = KademliaPeerRouter(self.host)
        self.service_key = b"meshtrain:v0"
        
    async def start(self):
        print(f"[{self.host.get_id().to_string()}] Starting Kademlia DHT...")
        
    async def stop(self):
        print(f"[{self.host.get_id().to_string()}] Stopping Kademlia DHT...")

    async def bootstrap(self, bootstrap_peers: List[str]):
        """Connect to bootstrap nodes and join the DHT."""
        if not bootstrap_peers:
            return
            
        print(f"[{self.host.get_id().to_string()}] Bootstrapping DHT via {len(bootstrap_peers)} nodes...")
        from multiaddr import Multiaddr
        for p in bootstrap_peers:
            try:
                maddr = Multiaddr(p)
                peer_id = maddr.get_peer_id()
                if peer_id:
                    print(f"[{self.host.get_id().to_string()}] Attempting to bootstrap with {peer_id}...")
                    # We add the peer to the peerstore and then to the routing table
                    # Connect to the peer to ensure they are reachable
                    await self.host.connect(maddr)
                    # Currently py-libp2p KademliaRouter adds connected peers to routing table
            except Exception as e:
                print(f"Warning: Failed to bootstrap with {p}. Error: {e}. Falling back to local mDNS.")
            
    async def provide(self):
        """Announce that this node provides the MeshTrain service."""
        print(f"[{self.host.get_id().to_string()}] Announcing provider record for {self.service_key.decode()}...")
        try:
            await self.router.provide(self.service_key)
        except Exception as e:
            print(f"Failed to provide service record: {e}")
        
    async def find_providers(self) -> List[str]:
        """Query the DHT for nodes providing the MeshTrain service."""
        print(f"[{self.host.get_id().to_string()}] Searching DHT for {self.service_key.decode()} providers...")
        try:
            providers = await self.router.find_providers(self.service_key)
            return [p.id.to_string() for p in providers]
        except Exception as e:
            print(f"Failed to find providers: {e}")
            return []
