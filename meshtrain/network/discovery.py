import socket
from zeroconf import ServiceInfo, Zeroconf

class Discovery:
    """mDNS Peer discovery mechanism for MeshTrain (V1/V2)."""
    
    def __init__(self, peer_id: str, port: int, multiaddr_base: str):
        self.peer_id = peer_id
        self.port = port
        self.multiaddr_base = multiaddr_base
        self.zeroconf = Zeroconf()
        self.service_type = "_meshtrain._tcp.local."
        self.service_name = f"{self.peer_id}.{self.service_type}"
        self.info = None

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def start_discovery(self):
        print(f"[{self.peer_id}] Starting mDNS discovery on {self.service_type}...")
        ip = self._get_local_ip()
        
        # Build libp2p Multiaddr for advertisement
        maddr = f"/ip4/{ip}/tcp/{self.port}/p2p/{self.peer_id}"
        
        self.info = ServiceInfo(
            self.service_type,
            self.service_name,
            addresses=[socket.inet_aton(ip)],
            port=self.port,
            properties={'peer_id': self.peer_id, 'maddr': maddr, 'version': '0.2.0'}
        )
        self.zeroconf.register_service(self.info)
        print(f"[{self.peer_id}] Announced via mDNS: {maddr}")

    def stop_discovery(self):
        if self.info:
            print(f"[{self.peer_id}] Unregistering mDNS service...")
            self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
