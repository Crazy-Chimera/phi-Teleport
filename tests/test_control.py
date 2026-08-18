"""
Tests for control layer components.
"""

from phi_teleport.control.elegance_evaluator import EleganceEvaluator
from phi_teleport.control.bridge_energy_optimizer import BridgeEnergyOptimizer
from phi_teleport.control.pontryagin_optimizer import PontryaginOptimizer
from phi_teleport.control.safety_monitor import SafetyMonitor
from phi_teleport.control.system_identifier import OnlineSystemIdentifier
from phi_teleport.control.elegance_trajectory_monitor import EleganceTrajectoryMonitor
from phi_teleport.control.convergence_monitor import ConvergenceMonitor
from phi_teleport.control.teleportation_controller import TeleportationController
from phi_teleport.quantum.qubit_array import QubitArray
from phi_teleport.quantum.informion_source import InformionSource


def test_elegance_evaluator():
    ev = EleganceEvaluator()
    e = ev.evaluate(complexity=10.0, consistency=0.9)
    assert e > 0
    assert ev.compare(1.0, 2.0) == -1


def test_bridge_energy_optimizer_reduces_energy():
    opt = BridgeEnergyOptimizer()
    t, profile, energy = opt.optimize(I0=1e-40, target_I=1e-35, duration=100, dt=0.1)
    assert energy > 0
    assert profile.shape == t.shape


def test_pontryagin_optimizer_reaches_target():
    opt = PontryaginOptimizer()
    t, I, u = opt.solve(I0=1e-40, I_target=1e-35, T=200, dt=0.1)
    assert I[-1] >= 1e-35


def test_safety_monitor_rollback():
    sm = SafetyMonitor()
    result = sm.check(fidelity=0.999990, stability=0.4)
    assert result['action'] == 'rollback'


def test_system_identifier_updates():
    sid = OnlineSystemIdentifier()
    sid.update(I_prev=0.1, I_next=0.11, u=0.5, dt=0.1)
    gamma_stim, gamma_decay = sid.get_params()
    assert gamma_stim > 0
    assert gamma_decay >= 0


def test_elegance_trajectory_monitor_detects_regression():
    mon = EleganceTrajectoryMonitor()
    mon.record(1.0)
    result = mon.record(1.05)
    assert result['regressed'] is True


def test_convergence_monitor_flags_flat_trajectory():
    cm = ConvergenceMonitor(min_iterations=10, window=5, slope_threshold=1e-3)
    for i in range(20):
        converged = cm.record(1.0)
    assert converged is True


def test_teleportation_controller_completes():
    qa = QubitArray(rows=4, cols=4)
    src = InformionSource(gamma_stim=0.3, gamma_dec=0.01)
    controller = TeleportationController(qubit_array=qa, informion_source=src)
    result = controller.run()
    assert result['status'] == 'completed'
    assert result['elegance'] < 1.0
