"""
Safety monitor for teleportation bridges.
"""

import time
import logging
from typing import Callable, Optional, Dict, Any


class SafetyMonitor:
    """Continuous safety evaluation of an active teleportation bridge.

    Parameters
    -
    fidelity_floor : float
        Minimum acceptable fidelity (0–1).
    stability_floor : float
        Minimum acceptable Ljapunov stability (normalized 0–1).
    rollback_timeout : float
        Maximum time allowed for a controlled rollback, in seconds.
    """

    def __init__(self, fidelity_floor: float = 0.999999,
                 stability_floor: float = 0.5,
                 rollback_timeout: float = 2.0):
        self.fidelity_floor = fidelity_floor
        self.stability_floor = stability_floor
        self.rollback_timeout = rollback_timeout
        self.logger = logging.getLogger(__name__)
        self.history = []

    def check(self, fidelity: float, stability: float) -> Dict[str, Any]:
        """Evaluate the current bridge state and return an action."""
        record = {
            'time': time.time(),
            'fidelity': fidelity,
            'stability': stability,
            'state': 'nominal',
        }
        if fidelity < self.fidelity_floor or stability < self.stability_floor:
            record['state'] = 'degraded'
            self.history.append(record)
            self.logger.warning(
                f"Safety degradation: fidelity={fidelity:.9f}, stability={stability:.3f}"
            )
            return {
                'action': 'rollback',
                'reason': 'fidelity_or_stability_below_floor',
                'rollback_timeout': self.rollback_timeout,
            }
        record['state'] = 'nominal'
        self.history.append(record)
        return {'action': 'continue'}

    def controlled_rollback(self, callback: Optional[Callable] = None) -> None:
        """Perform a controlled rollback by disconnecting the bridge gracefully."""
        self.logger.info("Starting controlled rollback.")
        time.sleep(min(self.rollback_timeout, 0.1))
        if callback:
            callback()
        self.logger.info("Controlled rollback complete.")

    @property
    def current_state(self) -> str:
        """Return the state of the most recent check."""
        if not self.history:
            return 'unknown'
        return self.history[-1]['state']
