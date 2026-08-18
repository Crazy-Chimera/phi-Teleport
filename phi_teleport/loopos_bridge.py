"""
LoopOS integration for the teleportation controller.
Wraps TeleportationController as a LoopObject.
"""

from typing import Any, Dict
from loopos.core import LoopObject


class TeleportationLoop(LoopObject):
    """LoopOS wrapper for the teleportation controller.

    This allows the Meta‑Loop to observe, evaluate, and mutate the teleportation
    subsystem like any other self‑improving component.
    """

    def __init__(self, controller):
        super().__init__("Teleportation")
        self.controller = controller
        self.state.setdefault('last_result', {})

    def observe(self, external_input: Dict[str, Any]) -> Dict[str, Any]:
        result = self.controller.run(
            target_position=external_input.get('target_position')
        )
        self.state['last_result'] = result
        metrics = {
            'status': result.get('status', 'aborted'),
            'elegance': result.get('elegance', float('inf')),
            'emergent_distance': result.get('emergent_distance', float('inf')),
        }
        return metrics

    def control(self, metrics, memory, policy):
        return {'action': 'done'}

    def evaluate(self, metrics):
        return metrics.get('elegance', float('inf'))

    def termination_condition(self, metrics):
        return metrics.get('status') in ('completed', 'aborted')
