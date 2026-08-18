"""
Self‑evolution loop for teleportation controllers.
"""

import logging
import copy
import random
from typing import Dict, Any, Tuple

from loopos.core import LoopObject


class TeleportationSelfEvolutionLoop(LoopObject):
    """Evolve the teleportation controller's hyperparameters using elegance.

    Parameters
    -
    controller : TeleportationController
        The controller to be evolved.
    param_ranges : dict
        Mapping of parameter names to (low, high) ranges.
    mutation_rate : float
        Probability of mutating each parameter in a proposal.
    max_proposals : int
        Number of candidate mutations to test per iteration.
    """

    def __init__(self, controller, param_ranges: Dict[str, Tuple[float, float]],
                 mutation_rate: float = 0.3, max_proposals: int = 5):
        super().__init__("TeleportationEvolution")
        self.controller = controller
        self.param_ranges = param_ranges
        self.mutation_rate = mutation_rate
        self.max_proposals = max_proposals
        self.best_elegance = float('inf')
        self.best_params = {}
        self.logger = logging.getLogger(__name__)
        self._capture_best_params()

    def _capture_best_params(self):
        for name in self.param_ranges:
            self.best_params[name] = getattr(self.controller, name, None)

    def observe(self, external_input):
        result = self.controller.run()
        current = result.get('elegance', float('inf'))
        return {'elegance': current}

    def control(self, metrics, memory, policy):
        current_elegance = metrics.get('elegance', float('inf'))
        if current_elegance < self.best_elegance:
            self.best_elegance = current_elegance
            self._capture_best_params()

        proposals = []
        for _ in range(self.max_proposals):
            candidate = copy.deepcopy(self.controller)
            for name, (low, high) in self.param_ranges.items():
                if random.random() < self.mutation_rate:
                    current = getattr(candidate, name)
                    new_value = random.uniform(low, high)
                    setattr(candidate, name, new_value)
            proposals.append(candidate)

        best_candidate = None
        best_candidate_elegance = current_elegance
        for candidate in proposals:
            result = candidate.run()
            elegance = result.get('elegance', float('inf'))
            if elegance < best_candidate_elegance:
                best_candidate_elegance = elegance
                best_candidate = candidate

        if best_candidate is not None and best_candidate_elegance < self.best_elegance:
            for name in self.param_ranges:
                setattr(self.controller, name, getattr(best_candidate, name))
            self.best_elegance = best_candidate_elegance
            self._capture_best_params()
            return {'action': 'mutated', 'new_elegance': best_candidate_elegance}

        return {'action': 'no_improvement', 'best_elegance': self.best_elegance}

    def evaluate(self, metrics):
        return metrics.get('elegance', float('inf'))

    def termination_condition(self, metrics):
        return False
