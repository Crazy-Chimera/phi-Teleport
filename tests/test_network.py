"""
Tests for network layer components.
"""

from phi_teleport.network.gate_network import GateNetwork
from phi_teleport.network.distributed_consensus import GossipGate
from phi_teleport.network.phi_map import PhiMap


def test_gate_network_shortest_path():
    net = GateNetwork(['A', 'B', 'C'])
    net.add_channel('A', 'B', 1.0)
    net.add_channel('B', 'C', 2.0)
    net.add_channel('A', 'C', 5.0)
    path, dist = net.shortest_path('A', 'C')
    assert path == ['A', 'B', 'C']
    assert dist == 3.0


def test_gossip_gate_converges_distance_table():
    a = GossipGate('A')
    b = GossipGate('B')
    c = GossipGate('C')
    a.add_neighbor('B', 1.0)
    b.add_neighbor('C', 2.0)
    a.gossip([b, c])
    b.gossip([a, c])
    c.gossip([a, b])
    assert a.distance_table.get('C', 999) == 3.0


def test_phi_map_update_and_decay():
    pm = PhiMap()
    pm.update('gate1', 0.9)
    assert pm.get_phi('gate1') > 0.8
    assert pm.average_phi() > 0.0


def test_phi_map_high_phi_gates():
    pm = PhiMap()
    pm.update('gate1', 0.9)
    pm.update('gate2', 0.2)
    high = pm.high_phi_gates(threshold=0.7)
    assert 'gate1' in high
    assert 'gate2' not in high
