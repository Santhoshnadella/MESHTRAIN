import os
import json
import time
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

class DynamicPricer:
    """Calculates dynamic costs for jobs based on model size and complexity."""
    
    @staticmethod
    def calculate_inference_cost(model_name: str, prompt_length: int, expected_output_length: int) -> float:
        # Base cost of 0.1 MeshCoin + 0.01 per token
        base = 0.1
        token_cost = (prompt_length + expected_output_length) * 0.01
        
        # Multiplier for large models
        multiplier = 1.0
        if "70b" in model_name.lower():
            multiplier = 5.0
        elif "8x7b" in model_name.lower():
            multiplier = 3.0
            
        return (base + token_cost) * multiplier

class SignedTransactionLedger:
    """
    A Cryptographic Shared Ledger for MeshCoin (V14).
    Replaces the local SQLite ledger with verifiable signed transactions.
    """
    
    def __init__(self, ledger_path=".meshtrain/shared_ledger.jsonl"):
        self.ledger_path = ledger_path
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        self.balances = {}
        self._load_ledger()
        
    def _load_ledger(self):
        """Loads and replays the transaction log to build current state."""
        self.balances = {"SYSTEM": 100000} # Genesis pool
        if not os.path.exists(self.ledger_path):
            return
            
        with open(self.ledger_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                tx = json.loads(line)
                self._apply_tx(tx)
                
    def _apply_tx(self, tx: dict):
        sender = tx["sender"]
        receiver = tx["receiver"]
        amount = tx["amount"]
        
        self.balances[sender] = self.balances.get(sender, 0) - amount
        self.balances[receiver] = self.balances.get(receiver, 0) + amount

    def verify_and_record_transaction(self, sender: str, receiver: str, amount: float, signature_b64: str, sender_pub_key_bytes: bytes) -> bool:
        """Verifies a transaction signature before applying it to the ledger."""
        if self.get_balance(sender) < amount and sender != "SYSTEM":
            print(f"[Ledger] Transaction failed: {sender} has insufficient funds.")
            return False
            
        # Verify signature
        tx_message = f"{sender}->{receiver}:{amount}"
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(sender_pub_key_bytes)
            signature = base64.b64decode(signature_b64)
            public_key.verify(signature, tx_message.encode('utf-8'))
        except (InvalidSignature, Exception) as e:
            print(f"[Ledger] SECURITY ALERT: Invalid transaction signature: {e}")
            return False
            
        # Valid signature, record it
        tx = {
            "timestamp": time.time(),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "signature": signature_b64
        }
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(tx) + "\n")
            
        self._apply_tx(tx)
        print(f"[Ledger] Transfer successful: {amount} MeshCoins from {sender} to {receiver}.")
        return True

    def get_balance(self, peer_id: str) -> float:
        """Get the current verified MeshCoin balance of a peer."""
        return self.balances.get(peer_id, 0.0)

