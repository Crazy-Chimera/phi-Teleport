"""
Predictive maintenance for teleportation gates.
"""

import time
from collections import defaultdict
from typing import List, Tuple, Optional


class PredictiveMaintenance:
    """Predict gate failures from Φ and channel quality trends.

    Parameters
    -
    failure_threshold : float
        Φ below which a gate is considered at risk.
    acceleration_threshold : float
        Maximum allowed positive decoherence acceleration.
    history_size : int
        Number of recent samples to keep per gate.
    """

    def __init__(self, failure_threshold: float = 0.3,
                 acceleration_threshold: float = 0.001,
                 history_size: int = 50):
        self.failure_threshold = failure_threshold
        self.acceleration_threshold = acceleration_threshold
        self.history_size = history_size
        self.history = defaultdict(list)

    def observe(self, gate_id: str, phi: float) -> Optional[str]:
        """Record a Φ sample and return a risk assessment for the gate."""
        now = time.time()
        hist = self.history[gate_id]
        hist.append((now, phi))
        if len(hist) > self.history_size:
            hist = hist[-self.history_size:]
            self.history[gate_id] = hist

        if phi < self.failure_threshold:
            return 'low_phi'

        if len(hist) >= 10:
            recent = hist[-10:]
            dt = recent[-1][0] - recent[0][0]
            if dt <= 0:
                return None
            dphi = recent[-1][1] - recent[0][1]
            first_derivative = dphi / dt

            mid = len(recent) // 2
            dphi_first = recent[mid][1] - recent[0][1]
            dt_first = recent[mid][0] - recent[0][0]
            first_derivative_first_half = dphi_first / dt_first if dt_first > 0 else 0
            dphi_second = recent[-1][1] - recent[mid][1]
            dt_second = recent[-1][0] - recent[mid][0]
            first_derivative_second_half = dphi_second / dt_second if dt_second > 0 else 0
            second_derivative = (first_derivative_second_half - first_derivative_first_half) / (dt / 2)

            if first_derivative < 0 and abs(second_derivative) > self.acceleration_threshold:
                return 'decoherence_accelerating'

        return None
