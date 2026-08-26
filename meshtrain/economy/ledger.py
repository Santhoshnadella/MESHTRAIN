import sqlite3
import os

class CreditLedger:
    """Internal SQLite ledger for MeshCoin Tokenomics (V9)."""
    
    def __init__(self, db_path=".meshtrain/ledger.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    peer_id TEXT PRIMARY KEY,
                    balance INTEGER DEFAULT 0
                )
            ''')
            # Initialize local system account with 100 starter coins
            cursor.execute("INSERT OR IGNORE INTO accounts (peer_id, balance) VALUES ('SYSTEM', 100)")
            conn.commit()
            
    def credit(self, peer_id: str, amount: int = 1):
        """Add MeshCoins to a peer's account after successful verified compute."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (peer_id, balance) 
                VALUES (?, ?) 
                ON CONFLICT(peer_id) DO UPDATE SET balance = balance + ?
            ''', (peer_id, amount, amount))
            conn.commit()
            
    def debit(self, peer_id: str, amount: int = 1):
        """Remove MeshCoins from a peer's account."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (peer_id, balance) 
                VALUES (?, 0) 
                ON CONFLICT(peer_id) DO UPDATE SET balance = MAX(0, balance - ?)
            ''', (peer_id, amount))
            conn.commit()
            
    def get_balance(self, peer_id: str) -> int:
        """Get the current MeshCoin balance of a peer."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM accounts WHERE peer_id = ?", (peer_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
