"""
Logging System Module

Provides structured logging for drone movements, hazard detection,
survivor detection, and system state changes.
"""

import threading
import time
from typing import List, Dict, Optional
from collections import deque


class Logger:
    """
    Thread-safe in-memory logger for system events.
    
    Stores logs in memory with configurable max size.
    """
    
    def __init__(self, max_size: int = 100):
        self._logs: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def log(self, level: str, message: str, category: str = "SYSTEM") -> None:
        """
        Add a log entry.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            category: Event category
        """
        entry = {
            'timestamp': time.time(),
            'level': level,
            'category': category,
            'message': message
        }
        
        with self._lock:
            self._logs.append(entry)
    
    def info(self, message: str, category: str = "SYSTEM") -> None:
        """Log INFO level message."""
        self.log("INFO", message, category)
    
    def warning(self, message: str, category: str = "SYSTEM") -> None:
        """Log WARNING level message."""
        self.log("WARNING", message, category)
    
    def error(self, message: str, category: str = "SYSTEM") -> None:
        """Log ERROR level message."""
        self.log("ERROR", message, category)
    
    def debug(self, message: str, category: str = "SYSTEM") -> None:
        """Log DEBUG level message."""
        self.log("DEBUG", message, category)
    
    def get_all(self) -> List[Dict]:
        """Get all logs as list (copy for thread safety)."""
        with self._lock:
            return list(self._logs)
    
    def get_recent(self, count: int = 20) -> List[Dict]:
        """Get most recent N logs."""
        with self._lock:
            return list(self._logs)[-count:]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get logs filtered by category."""
        with self._lock:
            return [log for log in self._logs if log['category'] == category]
    
    def clear(self) -> None:
        """Clear all logs."""
        with self._lock:
            self._logs.clear()
    
    def get_count(self) -> int:
        """Get total log count."""
        with self._lock:
            return len(self._logs)


# Global logger instance
_system_logger = Logger(max_size=100)


def get_logger() -> Logger:
    """Get the global logger instance."""
    return _system_logger


def log_movement(drone_id: int, old_pos: tuple, new_pos: tuple, state: str) -> None:
    """Log drone movement event."""
    _system_logger.info(
        f"Drone {drone_id}: {old_pos} -> {new_pos} [{state}]",
        category="MOVEMENT"
    )


def log_hazard(drone_id: int, x: int, y: int, risk: str) -> None:
    """Log hazard detection event."""
    _system_logger.info(
        f"Drone {drone_id}: Hazard at ({x},{y}) [{risk}]",
        category="HAZARD"
    )


def log_survivor(drone_id: int, survivor_id: str, x: int, y: int) -> None:
    """Log survivor detection event."""
    _system_logger.info(
        f"Drone {drone_id}: Survivor {survivor_id} found at ({x},{y})",
        category="SURVIVOR"
    )


def log_state_change(drone_id: int, old_state: str, new_state: str) -> None:
    """Log drone state change."""
    _system_logger.info(
        f"Drone {drone_id}: {old_state} -> {new_state}",
        category="STATE"
    )


def log_system(message: str, level: str = "INFO") -> None:
    """Log general system event."""
    _system_logger.log(level, message, category="SYSTEM")