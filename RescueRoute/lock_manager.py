class LockManager:
    def __init__(self):
        # Maps item_id -> {"txn_id": str, "lock_type": "SHARED" or "EXCLUSIVE"}
        self.locks = {}
        
        # Wait-For Graph: maps txn_id -> set of txn_ids it is waiting for
        self.wait_for_graph = {}

    def acquire_lock(self, txn_id, item_id, lock_type="EXCLUSIVE"):
        """Attempts to acquire a lock on an item for a transaction."""
        if item_id not in self.locks:
            self.locks[item_id] = {"txn_id": txn_id, "lock_type": lock_type}
            print(f"[LockManager] Txn {txn_id} acquired {lock_type} lock on Item {item_id}.")
            return True
        
        current_holder = self.locks[item_id]["txn_id"]
        
        if current_holder == txn_id:
            print(f"[LockManager] Txn {txn_id} already holds lock on Item {item_id}.")
            return True

        # Conflict detected: Add edge to Wait-For Graph (Txn is waiting for current_holder)
        if txn_id not in self.wait_for_graph:
            self.wait_for_graph[txn_id] = set()
        self.wait_for_graph[txn_id].add(current_holder)
        
        print(f"[LockManager] CONFLICT: Txn {txn_id} must WAIT for Txn {current_holder} on Item {item_id}.")
        return False

    def release_locks(self, txn_id):
        """Releases all locks held by a transaction and updates the WFG."""
        released_items = []
        for item_id, lock_info in list(self.locks.items()):
            if lock_info["txn_id"] == txn_id:
                del self.locks[item_id]
                released_items.append(item_id)
        
        # Clean up wait-for graph entries
        if txn_id in self.wait_for_graph:
            del self.wait_for_graph[txn_id]
            
        for waiter, waiting_set in self.wait_for_graph.items():
            if txn_id in waiting_set:
                waiting_set.remove(txn_id)

        print(f"[LockManager] Txn {txn_id} released locks on items: {released_items}")

    def detect_deadlock(self):
        """Uses Cycle Detection on the Wait-For Graph to find deadlocks."""
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.wait_for_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True # Cycle found! Deadlock!
            
            rec_stack.remove(node)
            return False

        for node in list(self.wait_for_graph.keys()):
            if node not in visited:
                if dfs(node):
                    return True # Deadlock exists
        return False

# Quick test if run directly
if __name__ == "__main__":
    lm = LockManager()
    lm.acquire_lock("TXN-1", "ITEM-101", "EXCLUSIVE")
    lm.acquire_lock("TXN-2", "ITEM-101", "EXCLUSIVE") # Should cause a conflict/wait
    print("Deadlock detected?", lm.detect_deadlock())