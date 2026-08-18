"""
Redundant entanglement channel group.
A teleportation bridge uses three independent informion channels.
"""

from typing import List, Optional
from phi_teleport.quantum.entanglement_channel import EntanglementChannel


class RedundantChannelGroup:
    """A group of three independent channels, from which the best is chosen."""

    def __init__(self, initial_information: float = 1e-40):
        self.channels: List[EntanglementChannel] = [
            EntanglementChannel(initial_information),
            EntanglementChannel(initial_information),
            EntanglementChannel(initial_information),
        ]
        self.active_channel: Optional[EntanglementChannel] = None

    def activate_best(self, object_radius: float) -> EntanglementChannel:
        """Choose the channel with the shortest emergent distance."""
        traversable = [c for c in self.channels if c.is_traversable(object_radius)]
        if traversable:
            self.active_channel = min(traversable, key=lambda c: c.distance())
        else:
            self.active_channel = max(self.channels, key=lambda c: c.information)
        return self.active_channel

    def update_all(self, delta_I: float) -> None:
        """Update all three channels by the same delta."""
        for channel in self.channels:
            channel.update(delta_I)

    def best_distance(self) -> float:
        """Return the distance of the best (active) channel."""
        if self.active_channel is None:
            return min(c.distance() for c in self.channels)
        return self.active_channel.distance()

    def is_traversable(self, object_radius: float) -> bool:
        """Return True if any channel is traversable."""
        return any(c.is_traversable(object_radius) for c in self.channels)
