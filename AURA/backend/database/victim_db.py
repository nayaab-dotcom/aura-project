"""
Victim Database Module

Central in-memory storage for all detected survivors.
Thread-safe implementation for concurrent access.
"""

import threading
from typing import List, Optional, Dict


class VictimDB:
    """
    Thread-safe in-memory database for survivor records.
    
    Provides synchronized access to survivor data for
    multi-threaded drone operations.
    """
    
    def __init__(self):
        """Initialize empty survivor database."""
        self._survivors: List[Dict] = []
        self._lock = threading.Lock()
        self._id_counter = 0
    
    def add_survivor(self, survivor: Dict) -> None:
        """
        Add a survivor to the database.
        
        Args:
            survivor: Survivor dictionary record
        """
        with self._lock:
            self._survivors.append(survivor)
            self._id_counter += 1
    
    def get_all(self) -> List[Dict]:
        """
        Return all survivors (copy for thread safety).
        
        Returns:
            List of all survivor dictionaries.
        """
        with self._lock:
            return self._survivors.copy()
    
    def get_count(self) -> int:
        """
        Return total survivor count.
        
        Returns:
            Number of survivors in database.
        """
        with self._lock:
            return len(self._survivors)
    
    def get_by_id(self, survivor_id: str) -> Optional[Dict]:
        """
        Get survivor by their unique ID.
        
        Args:
            survivor_id: Survivor ID string
        
        Returns:
            Survivor dictionary or None if not found.
        """
        with self._lock:
            for survivor in self._survivors:
                if survivor['id'] == survivor_id:
                    return survivor
        return None
    
    def get_by_location(self, x: int, y: int, radius: float = 1.0) -> List[Dict]:
        """
        Get all survivors within radius of coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius
        
        Returns:
            List of nearby survivors.
        """
        from utils.helpers import calculate_distance
        
        nearby = []
        with self._lock:
            for survivor in self._survivors:
                dist = calculate_distance((x, y), (survivor['x'], survivor['y']))
                if dist <= radius:
                    nearby.append(survivor)
        return nearby
    
    def remove(self, survivor_id: str) -> bool:
        """
        Remove a survivor by ID.
        
        Args:
            survivor_id: Survivor ID to remove
        
        Returns:
            True if removed, False if not found.
        """
        with self._lock:
            for i, survivor in enumerate(self._survivors):
                if survivor['id'] == survivor_id:
                    self._survivors.pop(i)
                    return True
        return False
    
    def reset(self) -> None:
        """Clear all survivors for new mission."""
        with self._lock:
            self._survivors.clear()
            self._id_counter = 0
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with survivor counts and stats.
        """
        import time
        
        with self._lock:
            total = len(self._survivors)
            verified = sum(1 for s in self._survivors if s.get('status') == 'VERIFIED')
            
            if self._survivors:
                latest = max(s['timestamp'] for s in self._survivors)
                earliest = min(s['timestamp'] for s in self._survivors)
            else:
                latest = earliest = time.time()
            
            return {
                'total_survivors': total,
                'verified': verified,
                'unverified': total - verified,
                'mission_duration': latest - earliest
            }
