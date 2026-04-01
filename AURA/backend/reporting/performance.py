"""
Performance Metrics Module

Tracks system performance during simulation.
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class PerformanceMetrics:
    """Stores performance metrics for the simulation."""
    start_time: float = field(default_factory=time.time)
    tick_count: int = 0
    coverage_history: List[float] = field(default_factory=list)
    path_lengths: List[int] = field(default_factory=list)
    idle_ticks: int = 0
    
    def tick(self, visited_count: int, total_cells: int, path_length: int = 0):
        """Record metrics for a single tick."""
        self.tick_count += 1
        coverage = (visited_count / total_cells) * 100 if total_cells > 0 else 0
        self.coverage_history.append(coverage)
        if path_length > 0:
            self.path_lengths.append(path_length)
    
    def record_idle(self):
        """Record an idle tick."""
        self.idle_ticks += 1
    
    def get_rate(self) -> float:
        """Get coverage rate (cells per second)."""
        if self.tick_count == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0
        current_coverage = self.coverage_history[-1] if self.coverage_history else 0
        return (current_coverage / 100 * 2500) / elapsed
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        elapsed = time.time() - self.start_time
        
        avg_path = sum(self.path_lengths) / len(self.path_lengths) if self.path_lengths else 0
        
        current_coverage = self.coverage_history[-1] if self.coverage_history else 0
        
        return {
            'elapsed_seconds': round(elapsed, 1),
            'total_ticks': self.tick_count,
            'current_coverage_percent': round(current_coverage, 2),
            'coverage_rate_cells_per_sec': round(self.get_rate(), 2),
            'avg_path_length': round(avg_path, 1),
            'idle_ticks': self.idle_ticks,
            'coverage_at_60s': self._get_coverage_at(60),
            'coverage_at_120s': self._get_coverage_at(120)
        }
    
    def _get_coverage_at(self, seconds: float) -> float:
        """Get coverage percentage at a specific elapsed time."""
        if seconds <= 0 or not self.coverage_history:
            return 0.0
        estimated_tick = int(seconds)
        if estimated_tick < len(self.coverage_history):
            return round(self.coverage_history[estimated_tick], 2)
        return round(self.coverage_history[-1], 2)


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
    
    def update(self, visited_count: int, total_cells: int, path_length: int = 0):
        """Update metrics for current tick."""
        self.metrics.tick(visited_count, total_cells, path_length)
    
    def add_idle(self):
        """Record an idle tick."""
        self.metrics.record_idle()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        return self.metrics.get_summary()
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = PerformanceMetrics()