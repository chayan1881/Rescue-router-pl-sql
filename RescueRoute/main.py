import time
from storage_node import StorageNode
from lock_manager import LockManager
from ml_predictor import DeadlockPredictor

class DatabaseOrchestrator:
    def __init__(self):
        print("--- Initializing Distributed ADBMS Engine ---")
        # Initialize regional warehouse nodes
        self.nodes = {
            "North": StorageNode("North"),
            "South": StorageNode("South")
        }
        
        # Seed initial inventories
        self.nodes["North"].seed_initial_data([
            {"item_id": "ITEM-101", "item_name": "Wireless Mouse", "stock_level": 25, "reorder_threshold": 10},
            {"item_id": "ITEM-102", "item_name": "Mechanical Keyboard", "stock_level": 8, "reorder_threshold": 10}
        ])
        
        self.lock_manager = LockManager()
        self.ml_predictor = DeadlockPredictor()

    def run_active_trigger_check(self, warehouse_id, item_id):
        """Active Database Trigger: Checks if stock dropped below reorder threshold."""
        node = self.nodes[warehouse_id]
        item = node.read_stock(item_id)
        if item and item['stock_level'] <= item['reorder_threshold']:
            print(f"\n🔥 [ACTIVE TRIGGER FIRED!] Item '{item['item_name']}' ({item_id}) in Warehouse '{warehouse_id}' "
                  f"has stock level {item['stock_level']} <= threshold {item['reorder_threshold']}. "
                  f"Automated Restock Order Generated!\n")

    def execute_transaction(self, txn_id, warehouse_id, item_id, new_stock_level, txn_metrics):
        print(f"\n==============================================")
        print(f"Starting Transaction: {txn_id} on Warehouse {warehouse_id}")
        print(f"==============================================")
        
        # 1. ML Predictive Deadlock Check
        risk = self.ml_predictor.predict_risk(
            item_count=txn_metrics['item_count'],
            write_ratio=txn_metrics['write_ratio'],
            concurrent_txn_count=txn_metrics['concurrent_txn_count'],
            wait_time_ms=txn_metrics['wait_time_ms']
        )
        
        print(f"[ML Engine] Risk Analysis for {txn_id}: {risk['risk_probability']}% Deadlock Probability")
        
        if risk['risk_probability'] > 70.0:
            print(f"⚠️ [PREEMPTIVE ACTION] {txn_id} flagged as HIGH RISK! Staggering transaction execution to prevent deadlock.")
            time.sleep(0.5) # Preemptive delay to break potential cycle

        # 2. Concurrency Control: Acquire Lock
        lock_acquired = self.lock_manager.acquire_lock(txn_id, item_id, lock_type="EXCLUSIVE")
        
        if not lock_acquired:
            print(f"⏳ {txn_id} is blocked and waiting for lock release...")
            # Check for deadlocks using Wait-For Graph
            if self.lock_manager.detect_deadlock():
                print(f"🛑 [DEADLOCK DETECTED] Cycle found in Wait-For Graph! Aborting {txn_id}.")
                self.lock_manager.release_locks(txn_id)
                return False

        try:
            # 3. Storage Layer Update with Write-Ahead Logging (WAL)
            node = self.nodes[warehouse_id]
            node.update_stock_with_wal(txn_id, item_id, new_stock_level)
            
            # 4. Fire Active Database Triggers
            self.run_active_trigger_check(warehouse_id, item_id)
            
            print(f"✅ Transaction {txn_id} committed successfully.")
        except Exception as e:
            print(f"❌ Transaction {txn_id} failed: {e}")
        finally:
            # 5. Release Locks upon completion
            self.lock_manager.release_locks(txn_id)

if __name__ == "__main__":
    db = DatabaseOrchestrator()

    # Simulate Transaction 1: Normal update on item 101 (Low risk)
    db.execute_transaction(
        txn_id="TXN-A1", 
        warehouse_id="North", 
        item_id="ITEM-101", 
        new_stock_level=20, 
        txn_metrics={'item_count': 1, 'write_ratio': 0.3, 'concurrent_txn_count': 2, 'wait_time_ms': 5}
    )

    # Simulate Transaction 2: Heavy bulk update triggering the Active Trigger on item 102 (Stock is 8, threshold is 10)
    db.execute_transaction(
        txn_id="TXN-A2", 
        warehouse_id="North", 
        item_id="ITEM-102", 
        new_stock_level=4, 
        txn_metrics={'item_count': 4, 'write_ratio': 0.8, 'concurrent_txn_count': 9, 'wait_time_ms': 140}
    )