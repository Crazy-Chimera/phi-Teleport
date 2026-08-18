"""
Asymptotic convergence monitor.
"""

import time
from typing import List, Tuple


class ConvergenceMonitor:
    """Detect asymptotic convergence of elegance scores.

    Parameters
    -
    window : int
        Number of recent scores to use for slope estimation.
    slope_threshold : float
        Maximum absolute slope of the elegance trajectory that is
        considered flat.
    min_iterations : int
        Minimum number of iterations before convergence can be declared.
    """

    def __init__(self, window: int = 20, slope_threshold: float = 1e-6,
                 min_iterations: int = 50):
        self.window = window
        self.slope_threshold = slope_threshold
        self.min_iterations = min_iterations
        self.history: List[Tuple[float, float]] = []

    def record(self, elegance: float) -> bool:
        """Record a new elegance score and return True if converged."""
        self.history.append((time.time(), elegance))
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        if len(self.history) < self.min_iterations:
            return False

        recent = self.history[-self.window:]
        t = [x[0] for x in recent]
        e = [x[1] for x in recent]
        n = len(t)
        if n < 2:
            return False
        t_mean = sum(t) / n
        e_mean = sum(e) / n
        num = sum((t[i] - t_mean) * (e[i] - e_mean) for i in range(n))
        den = sum((t[i] - t_mean) ** 2 for i in range(n))
        if den == 0:
            slope = 0.0
        else:
            slope = num / den

        return abs(slope) <= self.slope_threshold
