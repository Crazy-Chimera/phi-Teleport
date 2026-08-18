"""
Gossip‑based distributed consensus for teleportation gate networks.
"""

import random
import math
import time
from typing import Dict, List, Tuple, Set


class GossipGate:
    """A single gate participating in the gossip protocol.

    Parameters
    -
    gate_id : str
        Unique identifier of the gate.
    neighbors : list of str
        Direct neighbor gate IDs.
    """

    def __init__(self, gate_id: str, neighbors: List[str] = None):
        self.gate_id = gate_id
        self.neighbors: Set[str] = set(neighbors or [])
        self.distance_table: Dict[str, float] = {gate_id: 0.0}
        self.gossip_table: Dict[str, Dict[str, float]] = {}
        self.last_seen: Dict[str, float] = {}

    def add_neighbor(self, neighbor_id: str, distance: float) -> None:
        """Add or update a direct neighbor with an emergent distance."""
        self.neighbors.add(neighbor_id)
        self.distance_table[neighbor_id] = distance
        self.last_seen[neighbor_id] = time.time()

    def gossip(self, peers: List['GossipGate']) -> None:
        """Send our distance table to a random subset of peers and receive theirs."""
        selected = random.sample(peers, min(2, len(peers)))
        for peer in selected:
            peer.receive_gossip(self.gate_id, self.distance_table.copy())
            self.receive_gossip(peer.gate_id, peer.distance_table.copy())

    def receive_gossip(self, from_gate: str, distances: Dict[str, float]) -> None:
        """Incorporate a distance table from another gate."""
        self.gossip_table[from_gate] = distances.copy()
        self.last_seen[from_gate] = time.time()
        for dest, dist in distances.items():
            via_dist = self.distance_table.get(from_gate, math.inf) + dist
            current = self.distance_table.get(dest, math.inf)
            if via_dist < current:
                self.distance_table[dest] = via_dist

    def best_path(self, target: str) -> Tuple[List[str], float]:
        """Return the best known path to a target using local tables."""
        if target == self.gate_id:
            return [self.gate_id], 0.0
        best_dist = self.distance_table.get(target, math.inf)
        if best_dist == math.inf:
            return [], math.inf
        best_next = None
        for neighbor in self.neighbors:
            dist_neighbor_to_target = self.gossip_table.get(neighbor, {}).get(target, math.inf)
            if dist_neighbor_to_target + self.distance_table[neighbor] <= best_dist + 1e-12:
                best_next = neighbor
                best_dist = dist_neighbor_to_target + self.distance_table[neighbor]
        if best_next is None:
            return [], math.inf
        return [self.gate_id, best_next], best_dist
