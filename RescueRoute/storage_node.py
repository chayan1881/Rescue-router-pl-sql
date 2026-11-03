import sqlite3
import os
from datetime import datetime

class StorageNode:
    def __init__(self, warehouse_id):
        self.warehouse_id = warehouse_id
        self.db_name = f"warehouse_{warehouse_id.lower()}.db"
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initializes the inventory, transaction log, and write-ahead log tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Inventory Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_id TEXT PRIMARY KEY,
                item_name TEXT NOT NULL,
                stock_level INTEGER NOT NULL,
                reorder_threshold INTEGER NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Transaction Log Table (For Atomicity & Recovery)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_log (
                txn_id TEXT PRIMARY KEY,
                status TEXT NOT NULL, -- ACTIVE, COMMITTED, ABORTED
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Write-Ahead Log (WAL) Table for Crash Recovery
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS write_ahead_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                txn_id TEXT,
                operation TEXT, -- INSERT, UPDATE
                item_id TEXT,
                old_value INTEGER,
                new_value INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print(f"[StorageNode] Warehouse '{self.warehouse_id}' initialized with database: {self.db_name}")

    def seed_initial_data(self, items):
        """Seeds initial stock data into the warehouse."""
        conn = self.get_connection()
        cursor = conn.cursor()
        for item in items:
            cursor.execute("""
                INSERT OR REPLACE INTO inventory (item_id, item_name, stock_level, reorder_threshold, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (item['item_id'], item['item_name'], item['stock_level'], item['reorder_threshold'], datetime.now()))
        conn.commit()
        conn.close()
        print(f"[StorageNode] Seeded {len(items)} items into warehouse {self.warehouse_id}.")

    def read_stock(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_stock_with_wal(self, txn_id, item_id, new_stock):
        """Updates stock level using a Write-Ahead Log (WAL) entry for recovery."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get old value for WAL
        cursor.execute("SELECT stock_level FROM inventory WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Item {item_id} not found in warehouse {self.warehouse_id}")
        
        old_stock = row['stock_level']

        # 1. Write to WAL first
        cursor.execute("""
            INSERT INTO write_ahead_log (txn_id, operation, item_id, old_value, new_value)
            VALUES (?, 'UPDATE', ?, ?, ?)
        """, (txn_id, item_id, old_stock, new_stock))

        # 2. Perform actual update
        cursor.execute("""
            UPDATE inventory SET stock_level = ?, last_updated = ? WHERE item_id = ?
        """, (new_stock, datetime.now(), item_id))

        conn.commit()
        conn.close()
        print(f"[WAL] Txn {txn_id}: Logged update for Item {item_id} (Old: {old_stock} -> New: {new_stock})")

# Quick test if run directly
if __name__ == "__main__":
    node_north = StorageNode("North")
    node_north.seed_initial_data([
        {"item_id": "ITEM-101", "item_name": "Wireless Mouse", "stock_level": 50, "reorder_threshold": 10},
        {"item_id": "ITEM-102", "item_name": "Mechanical Keyboard", "stock_level": 30, "reorder_threshold": 5}
    ])
    print("Test Read:", node_north.read_stock("ITEM-101"))