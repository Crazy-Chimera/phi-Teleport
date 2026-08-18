"""
Multi‑gate teleportation network.
"""

import heapq
from typing import Dict, List, Tuple, Optional


class GateNetwork:
    """A network of teleportation gates connected by entanglement channels.

    Parameters
    -
    gates : list of str
        Identifiers of the gates.
    """

    def __init__(self, gates: List[str] = None):
        self.adjacency: Dict[str, Dict[str, float]] = {}
        if gates:
            for g in gates:
                self.adjacency.setdefault(g, {})

    def add_gate(self, gate_id: str) -> None:
        """Add a new gate to the network."""
        self.adjacency.setdefault(gate_id, {})

    def add_channel(self, from_gate: str, to_gate: str, distance: float) -> None:
        """Add or update an entanglement channel between two gates."""
        self.adjacency.setdefault(from_gate, {})
        self.adjacency.setdefault(to_gate, {})
        self.adjacency[from_gate][to_gate] = distance
        self.adjacency[to_gate][from_gate] = distance

    def shortest_path(self, source: str, target: str) -> Tuple[List[str], float]:
        """Return the shortest path and its total distance using Dijkstra."""
        dist = {node: float('inf') for node in self.adjacency}
        prev = {node: None for node in self.adjacency}
        dist[source] = 0.0
        pq = [(0.0, source)]

        while pq:
            current_dist, current = heapq.heappop(pq)
            if current_dist > dist[current]:
                continue
            for neighbor, weight in self.adjacency[current].items():
                candidate = current_dist + weight
                if candidate < dist[neighbor]:
                    dist[neighbor] = candidate
                    prev[neighbor] = current
                    heapq.heappush(pq, (candidate, neighbor))

        if dist[target] == float('inf'):
            return [], float('inf')

        path = []
        node = target
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()
        return path, dist[target]

    def all_paths(self) -> Dict[Tuple[str, str], Tuple[List[str], float]]:
        """Return shortest paths for all gate pairs."""
        paths = {}
        for source in self.adjacency:
            for target in self.adjacency:
                if source == target:
                    continue
                path, dist = self.shortest_path(source, target)
                paths[(source, target)] = (path, dist)
        return paths
