"""
Extended Kalman Filter for dynamic teleportation targets.
Handles acceleration in addition to position and velocity.
"""

import numpy as np
from typing import Tuple


class EKFDynamicTargetTracker:
    """Tracks a moving target using an extended Kalman filter.

    State vector: [x, y, z, vx, vy, vz, ax, ay, az]
    Measurement: [x, y, z] only.
    """

    def __init__(self, dt: float = 0.1,
                 process_noise_pos: float = 1e-6,
                 process_noise_vel: float = 1e-4,
                 process_noise_acc: float = 1e-2,
                 measurement_noise: float = 1e-3):
        self.dt = dt
        self.q = np.array([process_noise_pos, process_noise_vel, process_noise_acc])
        self.r = measurement_noise
        self.n_states = 9
        self.n_meas = 3

        self.x = np.zeros(self.n_states)   # initial state
        self.P = np.eye(self.n_states) * 0.1

        # Measurement matrix: observes position only
        self.H = np.zeros((self.n_meas, self.n_states))
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0

    def _state_transition(self, x: np.ndarray) -> np.ndarray:
        """State transition function f(x)."""
        pos = x[0:3]
        vel = x[3:6]
        acc = x[6:9]
        new_pos = pos + vel * self.dt + 0.5 * acc * self.dt**2
        new_vel = vel + acc * self.dt
        new_acc = acc  # assume constant acceleration over small dt
        return np.concatenate([new_pos, new_vel, new_acc])

    def _jacobian_F(self) -> np.ndarray:
        """Jacobian of the state transition."""
        F = np.eye(self.n_states)
        F[0, 3] = self.dt
        F[1, 4] = self.dt
        F[2, 5] = self.dt
        F[0, 6] = 0.5 * self.dt**2
        F[1, 7] = 0.5 * self.dt**2
        F[2, 8] = 0.5 * self.dt**2
        F[3, 6] = self.dt
        F[4, 7] = self.dt
        F[5, 8] = self.dt
        return F

    def predict(self, t_horizon: float = 0.0) -> np.ndarray:
        """Predict future position t_horizon seconds ahead."""
        pos = self.x[0:3]
        vel = self.x[3:6]
        acc = self.x[6:9]
        return pos + vel * t_horizon + 0.5 * acc * t_horizon**2

    def update(self, measurement: np.ndarray) -> None:
        """EKF update step."""
        measurement = np.asarray(measurement)

        # Predict
        F = self._jacobian_F()
        self.x = self._state_transition(self.x)
        Q = np.diag(np.tile(self.q, 3))
        self.P = F @ self.P @ F.T + Q

        # Update
        z = measurement
        h = self.H @ self.x
        y = z - h
        S = self.H @ self.P @ self.H.T + self.r * np.eye(self.n_meas)
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(self.n_states) - K @ self.H) @ self.P

    def phi_ping_strength(self) -> float:
        """Return a Φ-ping strength based on tracking covariance."""
        pos_cov = self.P[0:3, 0:3]
        return 1.0 / (1.0 + np.trace(pos_cov))
