#!/usr/bin/env python3
"""
Gate network routing example.

Creates a network of teleportation gates, adds channels with
different emergent distances, and finds the shortest path.
"""

from phi_teleport.network.gate_network import GateNetwork
from phi_teleport.network.distributed_consensus import GossipGate
from phi_teleport.network.phi_map import PhiMap

def main():
    print("Φ‑Teleport Network Routing Example")
    print("=" * 50)

    # Create a gate network with 5 gates.
    net = GateNetwork(['Prague', 'Brno', 'Berlin', 'Vienna', 'Paris'])
    net.add_channel('Prague', 'Brno', 1.0)
    net.add_channel('Prague', 'Berlin', 3.0)
    net.add_channel('Brno', 'Vienna', 2.0)
    net.add_channel('Vienna', 'Paris', 4.0)
    net.add_channel('Berlin', 'Paris', 2.0)

    # Find the shortest path from Prague to Paris.
    path, dist = net.shortest_path('Prague', 'Paris')
    print(f"Shortest path from Prague to Paris: {' -> '.join(path)}")
    print(f"Total emergent distance: {dist:.2f} m")

    # Demonstrate distributed consensus.
    print("\nDistributed consensus:")
    a = GossipGate('Prague')
    b = GossipGate('Brno')
    c = GossipGate('Vienna')
    a.add_neighbor('Brno', 1.0)
    b.add_neighbor('Vienna', 2.0)

    # Gossip round.
    a.gossip([b, c])
    b.gossip([a, c])
    c.gossip([a, b])

    print(f"Prague distance table: {a.distance_table}")

    # Demonstrate global Φ-map.
    print("\nGlobal Φ-map:")
    phi_map = PhiMap()
    phi_map.update('Prague', 0.85)
    phi_map.update('Brno', 0.72)
    phi_map.update('Berlin', 0.55)
    phi_map.update('Vienna', 0.80)
    phi_map.update('Paris', 0.78)

    print(f"Average Φ: {phi_map.average_phi():.3f}")
    print(f"High‑Φ gates (threshold 0.7): {phi_map.high_phi_gates(0.7)}")

if __name__ == '__main__':
    main()
