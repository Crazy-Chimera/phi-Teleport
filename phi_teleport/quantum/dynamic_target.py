"""
Dynamic target tracking for teleportation.
A moving target emits periodic Φ-pings that allow the source node
to predict its future position and maintain the entanglement bridge.
"""

import numpy as np
from typing import List, Tuple


class DynamicTargetTracker:
    """Tracks and predicts the position of a moving teleportation target.

    Uses a simple constant-velocity Kalman filter on position measurements.
    """

    def __init__(self, dt: float = 0.1, process_noise: float = 1e-3):
        self.dt = dt
        self.q = process_noise
        self.x = np.zeros(3)       # position [x, y, z]
        self.v = np.zeros(3)       # velocity [vx, vy, vz]
        self.P = np.eye(6) * 0.1   # covariance
        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0

    def predict(self, t_horizon: float = 0.0) -> np.ndarray:
        """Predict future position t_horizon seconds ahead."""
        return self.x + self.v * t_horizon

    def update(self, measurement: np.ndarray) -> None:
        """Update the tracker with a new position measurement."""
        measurement = np.asarray(measurement)
        # Predict step
        self.x = self.x + self.v * self.dt
        F = np.eye(6)
        F[0, 3] = self.dt
        F[1, 4] = self.dt
        F[2, 5] = self.dt
        self.P = F @ self.P @ F.T + self.q * np.eye(6)

        # Update step
        y = measurement - self.H @ np.r_[self.x, self.v]
        S = self.H @ self.P @ self.H.T + np.eye(3) * 0.1
        K = self.P @ self.H.T @ np.linalg.inv(S)
        state = np.r_[self.x, self.v] + K @ y
        self.x = state[:3]
        self.v = state[3:]
        self.P = (np.eye(6) - K @ self.H) @ self.P

    def phi_ping(self) -> float:
        """Return a nominal Φ-ping strength based on tracking uncertainty."""
        return 1.0 / (1.0 + np.trace(self.P[:3, :3]))
