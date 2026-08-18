"""
Single entanglement channel between two nodes.
"""

from phi_teleport.constants import PLANCK_LENGTH


class EntanglementChannel:
    """Represents one entanglement bridge channel.

    Parameters
    -
    initial_information : float
        Initial mutual information I₀.
    """

    def __init__(self, initial_information: float = 1e-40):
        self.information = initial_information

    def update(self, delta_I: float):
        """Update the mutual information by delta_I."""
        self.information = max(0.0, min(1.0, self.information + delta_I))

    def distance(self) -> float:
        """Return the emergent distance for the current information."""
        if self.information <= 0:
            return float('inf')
        return PLANCK_LENGTH / self.information

    def is_traversable(self, object_radius: float = 1.0) -> bool:
        """Return True if the channel is traversable for the given object radius."""
        return self.distance() < object_radius
