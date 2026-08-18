"""
Tests for simulation components.
"""

from phi_teleport.sim.full_lattice_simulation import FullLatticeSimulation
from phi_teleport.sim.lindblad_master_equation import LindbladChainSimulator


def test_full_lattice_simulation_decays():
    sim = FullLatticeSimulation(n_qubits=256, T1=1e-6, T2=5e-7)
    t, coh = sim.run(duration=1.0, dt=0.01)
    assert coh[-1] <= coh[0]


def test_lindblad_simulation_decays_concurrence():
    sim = LindbladChainSimulator(n_qubits=2, gamma_decay=0.05, gamma_dephase=0.02)
    t, conc = sim.run(duration=5.0, dt=0.01)
    assert conc[-1] <= conc[0]
