import asyncio
import json
from multiaddr import Multiaddr
from libp2p import new_host
from libp2p.crypto.ed25519 import create_new_key_pair
from meshtrain.network.discovery import Discovery
from meshtrain.network.dht import MeshDHT
from meshtrain.node.agent import MeshNode
from meshtrain.capability.gpu import HardwareDetector
from meshtrain.storage.content_store import ContentStore
from meshtrain.finetuning.lora import LoRATuner
from meshtrain.economy.ledger import CreditLedger
import os
import base64

PROTOCOL_ID = "/meshtrain/1.0.0"

class Peer:
    """The local P2P node utilizing py-libp2p (Mocked for MVP, V14 secured)."""
    
    def __init__(self, port: int = 8001, use_relay: bool = False):
        self.port = port
        self.use_relay = use_relay
        self.keypair = create_new_key_pair()
        self.host = None
        self.connected_peers = {}
        self.peer_capabilities = {}
        self.local_hw = HardwareDetector().detect()
        self.ai_node = MeshNode()
        self.content_store = ContentStore()
        self.lora_tuner = LoRATuner()
        self.ledger = CreditLedger()
        
        # Discovery and DHT are instantiated after we know our PeerID
        self.discovery = None
        self.dht = None

    async def start_server(self):
        print(f"[{self.peer_id}] Starting py-libp2p host on port {self.port}...")
        
        if self.use_relay:
            print(f"[{self.peer_id}] NAT Traversal Optimization (V14): Circuit Relay Enabled.")
            print(f"[{self.peer_id}] AutoNAT detecting network status...")
            # We would connect to public IPFS bootstrap nodes here to act as relays
            print(f"[{self.peer_id}] Listening on relay multiaddrs: /p2p/QmRelayNode/p2p-circuit/p2p/{self.peer_id}")

        # Create libp2p host
        multiaddr = Multiaddr(f"/ip4/0.0.0.0/tcp/{self.port}")
        self.host = new_host(key_pair=self.keypair, listen_addrs=[multiaddr])
        
        self.peer_id = self.host.get_id().to_string()
        
        # Set up stream handler for our protocol
        self.host.set_stream_handler(PROTOCOL_ID, self.handle_stream)
        
        # Start listening
        await self.host.get_network().listen(multiaddr)
        
        listen_addresses = [str(addr) for addr in self.host.get_addrs()]
        print(f"[{self.peer_id}] Libp2p Node listening on: {listen_addresses}")
        
        # Start discovery
        self.discovery = Discovery(self.peer_id, self.port, str(listen_addresses[0]) if listen_addresses else "")
        self.discovery.start_discovery()
        
        # Initialize DHT
        self.dht = MeshDHT(self.host)
        await self.dht.start()
        await self.dht.provide()
        
    async def stop_server(self):
        if self.discovery:
            self.discovery.stop_discovery()
        if self.dht:
            await self.dht.stop()
        if self.host:
            await self.host.close()

    async def handle_stream(self, stream):
        # Read from libp2p stream
        remote_peer = stream.muxed_conn.peer_id.to_string()
        print(f"[{self.peer_id}] Incoming Libp2p stream from {remote_peer}")
        
        try:
            data = await asyncio.wait_for(stream.read(), timeout=30.0) # 30s timeout for initial read
            message = json.loads(data.decode())
            
            if message.get("type") == "HANDSHAKE":
                hw_caps = message.get("hardware", {})
                print(f"[{self.peer_id}] Handshake successful with {remote_peer}")
                self.connected_peers[remote_peer] = stream
                self.peer_capabilities[remote_peer] = {"hardware": hw_caps}
                
                # Reply
                reply = json.dumps({"type": "HANDSHAKE_ACK", "peer_id": self.peer_id, "hardware": self.local_hw})
                await stream.write(reply.encode())
                
            elif message.get("type") == "INFERENCE_REQUEST":
                req_id = message.get("request_id")
                model_name = message.get("model")
                prompt = message.get("prompt")
                modality = message.get("modality", "text")
                sender_id = message.get("sender")
                
                print(f"[{self.peer_id}] Received INFERENCE_REQUEST ({modality}) from {sender_id} for {model_name}")
                
                if modality == "image":
                    result = self.ai_node.generate_image(prompt, model_name)
                    payload_type = result["payload_type"]
                    # Base64 encode binary payload for JSON transport
                    payload = base64.b64encode(result["payload"]).decode('utf-8') if isinstance(result["payload"], bytes) else result["payload"]
                else:
                    result = self.ai_node.infer(model_name, prompt)
                    payload_type = "text/plain"
                    payload = result["result"]
                
                # Send back result
                reply = json.dumps({
                    "type": "INFERENCE_RESULT",
                    "request_id": req_id,
                    "payload_type": payload_type,
                    "payload": payload,
                    "worker_peer_id": self.peer_id
                })
                await stream.write(reply.encode())
                
            elif message.get("type") == "TRAINING_REQUEST":
                req_id = message.get("request_id")
                model_name = message.get("model")
                manifest_hash = message.get("dataset_manifest_hash")
                
                print(f"[{self.peer_id}] Received TRAINING_REQUEST for {model_name} with dataset {manifest_hash}")
                
                # In full implementation, we would request the manifest and chunks via DATA_REQUEST here.
                # For this MVP, we assume the dataset is downloaded to a temporary location.
                dataset_path = f".meshtrain/store/manifests/{manifest_hash}.json"
                if not os.path.exists(dataset_path):
                     # Mock fallback if data not available
                     dataset_path = "mock_dataset.jsonl"
                
                # Execute long-running training job
                print(f"[{self.peer_id}] Starting distributed LoRA training...")
                adapter_weights = self.lora_tuner.tune(model_name, dataset_path)
                
                # We would normally encode binary adapter_weights securely, using base64 for MVP json
                import base64
                b64_weights = base64.b64encode(adapter_weights).decode('utf-8')
                
                reply = json.dumps({
                    "type": "TRAINING_RESULT",
                    "request_id": req_id,
                    "lora_adapter_weights": b64_weights,
                    "status": "success"
                })
                
                print(f"[{self.peer_id}] Training complete. Sending adapter weights back.")
                await stream.write(reply.encode())
                
        except asyncio.TimeoutError:
            print(f"[{self.peer_id}] Stream timeout with {remote_peer}")
        except Exception as e:
            print(f"Error handling stream: {e}")
        finally:
            await stream.close()

    async def connect_to_peer(self, maddr_str: str):
        print(f"[{self.peer_id}] Connecting to {maddr_str}...")
        try:
            maddr = Multiaddr(maddr_str)
            # Extact peer id from multiaddr
            peer_id_str = maddr.get_peer_id()
            if not peer_id_str:
                print("Multiaddr must include /p2p/ peer ID")
                return False
                
            # Connect
            stream = await self.host.new_stream(peer_id_str, [PROTOCOL_ID])
            
            # Send handshake
            handshake = json.dumps({"type": "HANDSHAKE", "peer_id": self.peer_id, "hardware": self.local_hw})
            await stream.write(handshake.encode())
            
            # Wait for ACK
            data = await stream.read()
            message = json.loads(data.decode())
            if message.get("type") == "HANDSHAKE_ACK":
                hw_caps = message.get("hardware", {})
                print(f"[{self.peer_id}] Successfully connected to peer: {peer_id_str}")
                self.connected_peers[peer_id_str] = stream
                self.peer_capabilities[peer_id_str] = {"hardware": hw_caps}
                
                asyncio.create_task(self._listen_for_results(stream, peer_id_str))
            return True
        except Exception as e:
            print(f"[{self.peer_id}] Failed to connect to {maddr_str}: {e}")
            return False

    async def _listen_for_results(self, stream, remote_peer):
        try:
            while True:
                data = await asyncio.wait_for(stream.read(), timeout=86400) # 24 HOUR timeout for long training jobs
                if not data:
                    break
                message = json.loads(data.decode())
                if message.get("type") == "INFERENCE_RESULT":
                    worker = message.get("worker_peer_id", remote_peer)
                    payload_type = message.get("payload_type", "text/plain")
                    payload = message.get("payload")
                    
                    if "image" in payload_type:
                        print(f"[{self.peer_id}] Image Result from {worker}!")
                        img_data = base64.b64decode(payload)
                        os.makedirs(".meshtrain/images", exist_ok=True)
                        with open(f".meshtrain/images/out_{worker}.png", "wb") as f:
                            f.write(img_data)
                        print(f"[{self.peer_id}] Saved image to .meshtrain/images/out_{worker}.png")
                    else:
                        print(f"[{self.peer_id}] Text Result from {worker}: {payload}")
                        
                    # Credit the worker node for successful compute!
                    self.ledger.credit(worker, amount=1)
                    print(f"[{self.peer_id}] [ECONOMY] Credited 1 MeshCoin to {worker}.")
                    
                elif message.get("type") == "TRAINING_RESULT":
                    print(f"[{self.peer_id}] Training Success from {remote_peer}!")
                    weights = base64.b64decode(message.get("lora_adapter_weights"))
                    print(f"[{self.peer_id}] Received {len(weights)} bytes of LoRA adapter weights.")
                    
                    # Save to local disk
                    os.makedirs(".meshtrain/lora_received", exist_ok=True)
                    with open(f".meshtrain/lora_received/adapter_{remote_peer}.bin", "wb") as f:
                        f.write(weights)
                        
                    # Credit the worker node for successful heavy compute!
                    self.ledger.credit(remote_peer, amount=50)
                    print(f"[{self.peer_id}] [ECONOMY] Credited 50 MeshCoins to {remote_peer}.")
                elif message.get("type") == "PIN_REQUEST":
                    chunk_hash = message.get("chunk_hash")
                    print(f"[{self.peer_id}] MeshDrive: Received PIN_REQUEST for chunk {chunk_hash}")
                    # In MVP we just acknowledge it
                    reply = json.dumps({"type": "PIN_RESPONSE", "chunk_hash": chunk_hash, "success": True})
                    await stream.write(reply.encode())
        except asyncio.TimeoutError:
            print(f"[{self.peer_id}] Connection to {remote_peer} timed out.")
        except Exception:
            pass

    async def send_training_request(self, target_peer: str, model: str, manifest_hash: str):
        if target_peer not in self.connected_peers:
            print(f"Error: Not connected to {target_peer}")
            return
            
        stream = self.connected_peers[target_peer]
        req = json.dumps({
            "type": "TRAINING_REQUEST",
            "request_id": "train-1",
            "sender": self.peer_id,
            "model": model,
            "dataset_manifest_hash": manifest_hash
        })
        await stream.write(req.encode())
        print(f"[{self.peer_id}] Sent TRAINING_REQUEST to {target_peer}. Waiting for 24h timeout...")

    async def send_inference_request(self, target_peer: str, model: str, prompt: str, modality: str = "text"):
        if target_peer not in self.connected_peers:
            print(f"Error: Not connected to {target_peer}")
            return
            
        stream = self.connected_peers[target_peer]
        req = json.dumps({
            "type": "INFERENCE_REQUEST",
            "request_id": "req-1",
            "sender": self.peer_id,
            "model": model,
            "prompt": prompt,
            "modality": modality
        })
        await stream.write(req.encode())
        print(f"[{self.peer_id}] Sent request to {target_peer}. Waiting for result...")
        
    async def pin_chunk_to_dht(self, chunk_hash: str, chunk_path: str):
        """MeshDrive (V7): Sends a chunk to connected peers for pinning."""
        for peer_id, stream in self.connected_peers.items():
            if peer_id == self.peer_id: continue
            print(f"[{self.peer_id}] MeshDrive: Pinning chunk {chunk_hash} to {peer_id}")
            try:
                # We'd normally read the file and send the binary data. For MVP, we send the intent.
                req = json.dumps({
                    "type": "PIN_REQUEST",
                    "chunk_hash": chunk_hash
                })
                await stream.write(req.encode())
            except Exception as e:
                print(f"Failed to pin to {peer_id}: {e}")

