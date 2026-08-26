import sqlite3
import os

class LocalStorage:
    """Local SQLite database for node state (V0)."""
    
    def __init__(self, db_path=".meshtrain/node.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artifacts (
                hash TEXT PRIMARY KEY,
                type TEXT,
                path TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def register_artifact(self, artifact_hash: str, artifact_type: str, path: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?)", (artifact_hash, artifact_type, path))
        conn.commit()
        conn.close()
