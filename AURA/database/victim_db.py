"""Thread-safe in-memory storage for detected survivors."""

import threading
import time
from typing import Dict, List, Optional


class VictimDB:
    """Thread-safe in-memory database for survivor records."""

    def __init__(self):
        self._survivors: List[Dict] = []
        self._lock = threading.Lock()
        self._id_counter = 0

    def add_survivor(self, survivor: Dict) -> Dict:
        """Add a survivor to the database, stamping missing fields as needed."""
        with self._lock:
            if "timestamp" not in survivor:
                survivor["timestamp"] = time.time()
            if "id" not in survivor:
                self._id_counter += 1
                survivor["id"] = f"VICTIM-{self._id_counter:05d}"
            self._survivors.append(survivor)
            return survivor

    def get_all(self) -> List[Dict]:
        """Return all survivors (copy for thread safety)."""
        with self._lock:
            return list(self._survivors)

    def get_count(self) -> int:
        """Return total survivor count."""
        with self._lock:
            return len(self._survivors)

    def get_by_id(self, survivor_id: str) -> Optional[Dict]:
        """Get survivor by their unique ID."""
        with self._lock:
            for survivor in self._survivors:
                if survivor["id"] == survivor_id:
                    return survivor
        return None

    def get_latest(self) -> Optional[Dict]:
        """Return the most recently detected survivor, if any."""
        with self._lock:
            if not self._survivors:
                return None
            return max(self._survivors, key=lambda s: s.get("timestamp", 0))

    def remove(self, survivor_id: str) -> bool:
        """Remove a survivor by ID."""
        with self._lock:
            for i, survivor in enumerate(self._survivors):
                if survivor["id"] == survivor_id:
                    self._survivors.pop(i)
                    return True
        return False

    def reset(self) -> None:
        """Clear all survivors for new mission."""
        with self._lock:
            self._survivors.clear()
            self._id_counter = 0
