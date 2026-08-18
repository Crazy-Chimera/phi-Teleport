"""
Elegance trajectory monitor.
"""

import time
from typing import List, Tuple


class EleganceTrajectoryMonitor:
    """Monitors the trajectory of elegance scores over teleportation runs.

    Parameters
    -
    window_size : int
        Number of past scores to keep for trend analysis.
    regression_tolerance : float
        Maximum allowed relative degradation compared to the best score
        before a regression is flagged.
    """

    def __init__(self, window_size: int = 100, regression_tolerance: float = 0.01):
        self.window_size = window_size
        self.tolerance = regression_tolerance
        self.history: List[Tuple[float, float]] = []  # (timestamp, elegance)
        self.best = float('inf')

    def record(self, elegance: float) -> dict:
        """Record a new elegance score and return a verdict."""
        now = time.time()
        previous_best = self.best
        if elegance < self.best:
            self.best = elegance

        self.history.append((now, elegance))
        if len(self.history) > self.window_size:
            self.history = self.history[-self.window_size:]

        relative_change = (elegance - previous_best) / max(previous_best, 1e-12)
        regressed = relative_change > self.tolerance

        return {
            'regressed': regressed,
            'best': self.best,
            'current': elegance,
            'relative_change': relative_change,
        }

    def is_converging(self) -> bool:
        """Return True if recent scores are not trending upward."""
        if len(self.history) < 2:
            return True
        recent = self.history[-5:]
        first = recent[0][1]
        last = recent[-1][1]
        return last <= first + 1e-9
