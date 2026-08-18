"""
Elegance evaluator for teleportation.
Computes E = C / K from complexity and consistency.
"""


class EleganceEvaluator:
    """Evaluates the elegance score of a teleportation operation.

    The elegance is E = C / K, where C is the total complexity and K
    is the consistency (fidelity, stability, absence of paradoxes).
    Lower E is better.
    """

    def __init__(self, complexity_weight: float = 1.0):
        self.complexity_weight = complexity_weight

    def evaluate(self, complexity: float, consistency: float) -> float:
        """Compute elegance from complexity and consistency.

        Parameters
        -
        complexity : float
            Total computational complexity C (energy, time, qubits).
        consistency : float
            Consistency K in (0, 1], where 1 is perfect.

        Returns
        -
        float
            Elegance score E = C / K.
        """
        if consistency <= 0:
            return float('inf')
        return self.complexity_weight * complexity / consistency

    def compare(self, e1: float, e2: float) -> int:
        """Return -1 if e1 is better, 1 if e2 is better, 0 if equal."""
        if e1 < e2:
            return -1
        elif e1 > e2:
            return 1
        return 0
