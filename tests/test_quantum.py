"""
Tests for quantum layer components.
"""

import numpy as np
from phi_teleport.quantum.qubit_array import QubitArray
from phi_teleport.quantum.informion_source import InformionSource
from phi_teleport.quantum.entanglement_channel import EntanglementChannel
from phi_teleport.quantum.redundant_channel import RedundantChannelGroup
from phi_teleport.quantum.decoherence_model import LindbladDecoherence
from phi_teleport.quantum.dynamic_target import DynamicTargetTracker
from phi_teleport.quantum.dynamic_target_ekf import EKFDynamicTargetTracker
from phi_teleport.quantum.async_sync_protocol import AsyncSyncProtocol


def test_qubit_array_dimensions():
    qa = QubitArray(rows=4, cols=4)
    assert qa.n_qubits == 16
    assert qa.J.shape == (16, 16)


def test_qubit_array_phi_range():
    qa = QubitArray(rows=2, cols=2)
    phi = qa.measure_local_phi()
    assert 0.0 <= phi <= 1.0


def test_emergent_distance():
    qa = QubitArray(rows=2, cols=2)
    d = qa.emergent_distance(1e-30)
    assert d > 0


def test_informion_source_growth():
    src = InformionSource(gamma_stim=0.2, gamma_dec=0.01)
    t, I = src.simulate(I0=1e-40, duration=100, dt=0.1)
    assert I[-1] > I[0]


def test_informion_critical_time():
    src = InformionSource(gamma_stim=0.3, gamma_dec=0.01)
    t_crit = src.critical_time(object_radius=1.0, duration=500, dt=0.1)
    assert t_crit is not None


def test_entanglement_channel_distance():
    ch = EntanglementChannel(initial_information=1e-35)
    assert ch.distance() > 0
    assert not ch.is_traversable(1.0)
    ch.update(1e-30)
    assert ch.is_traversable(1.0)


def test_redundant_channel_group_selects_best():
    group = RedundantChannelGroup(initial_information=1e-40)
    group.channels[1].information = 1e-30
    active = group.activate_best(object_radius=1.0)
    assert active is group.channels[1]
    assert group.is_traversable(1.0)


def test_lindblad_decoherence_phi_range():
    model = LindbladDecoherence(T1=1e-6, T2=5e-7)
    phi = model.estimate_phi()
    assert 0.0 <= phi <= 1.0


def test_dynamic_target_tracker_predicts():
    tracker = DynamicTargetTracker(dt=0.1)
    tracker.update([1.0, 2.0, 3.0])
    tracker.update([1.2, 2.1, 3.0])
    predicted = tracker.predict(t_horizon=1.0)
    assert predicted.shape == (3,)


def test_ekf_tracker_predicts_accelerating_target():
    tracker = EKFDynamicTargetTracker(dt=0.1)
    for i in range(20):
        acc = 0.1 * i
        pos = [0.5 * acc * (i*0.1)**2, 0.0, 0.0]
        tracker.update(pos)
    predicted = tracker.predict(t_horizon=1.0)
    assert predicted.shape == (3,)


def test_async_sync_returns_positive_latency():
    sync = AsyncSyncProtocol()
    latency = sync.synchronize("A", "B")
    assert latency >= 0
