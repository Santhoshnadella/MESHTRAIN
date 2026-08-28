import os
import base64
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Global connection to the free Devnet
SOLANA_RPC_URL = "https://api.devnet.solana.com"
solana_client = Client(SOLANA_RPC_URL)

# Our custom Smart Contract Program ID deployed on Devnet
# This matches the placeholder in Anchor.toml
MESHCOIN_PROGRAM_ID = Pubkey.from_string("FqD8y6HqA52554eJj9a8mD1XfAgh7vQp3R79h9U2M2Lw")

def get_solana_keypair(identity_file: str = ".meshtrain/identity.key") -> Keypair:
    """
    Derives a Solana Keypair directly from the node's existing ed25519 identity.
    This ensures that MeshTrain identities map 1:1 with Solana Wallets.
    """
    if not os.path.exists(identity_file):
        print(f"[SolanaConfig] Identity file {identity_file} not found. Generating a new one...")
        # Fallback if no identity file exists
        kp = Keypair()
        os.makedirs(os.path.dirname(identity_file), exist_ok=True)
        with open(identity_file, "w") as f:
            f.write(base64.b64encode(kp.secret()).decode('utf-8'))
        return kp

    with open(identity_file, "r") as f:
        # Load the base64 encoded private key (which we know is ed25519)
        priv_bytes = base64.b64decode(f.read().strip())
        
        try:
            # Reconstruct the Solders keypair from the raw bytes
            # Solders expects a 64-byte array (32 byte secret + 32 byte public)
            # If our identity only saved the 32-byte secret, we pad it or use from_seed
            if len(priv_bytes) == 32:
                return Keypair.from_seed(priv_bytes)
            else:
                return Keypair.from_bytes(priv_bytes)
        except Exception as e:
            print(f"[SolanaConfig] Error parsing identity file: {e}")
            return Keypair()

def request_airdrop(pubkey: Pubkey):
    """Requests free testing SOL from the Devnet faucet."""
    print(f"[SolanaConfig] Requesting airdrop for {pubkey}...")
    try:
        response = solana_client.request_airdrop(pubkey, 1_000_000_000) # 1 SOL
        print(f"[SolanaConfig] Airdrop signature: {response.value}")
    except Exception as e:
        print(f"[SolanaConfig] Airdrop failed: {e}")
