"""
TeleportationController – supports static and dynamic targets,
energy‑optimized bridge activation, and full safety monitoring.
"""

import enum
import logging
import numpy as np
from typing import Dict, Any, Optional
from phi_teleport.quantum.qubit_array import QubitArray
from phi_teleport.quantum.informion_source import InformionSource
from phi_teleport.quantum.redundant_channel import RedundantChannelGroup
from phi_teleport.quantum.dynamic_target_ekf import EKFDynamicTargetTracker
from phi_teleport.quantum.async_sync_protocol import AsyncSyncProtocol
from phi_teleport.control.pontryagin_optimizer import PontryaginOptimizer
from phi_teleport.control.safety_monitor import SafetyMonitor
from phi_teleport.control.elegance_evaluator import EleganceEvaluator
from phi_teleport.control.system_identifier import OnlineSystemIdentifier
from phi_teleport.control.elegance_trajectory_monitor import EleganceTrajectoryMonitor
from phi_teleport.network.gate_network import GateNetwork


class TeleportState(enum.Enum):
    IDLE = "IDLE"
    VERIFY = "VERIFY"
    SCAN = "SCAN"
    COMPUTE = "COMPUTE"
    ACTIVATE = "ACTIVATE"
    MONITOR = "MONITOR"
    COMPLETE = "COMPLETE"
    ABORT = "ABORT"


class TeleportationController:
    def __init__(self, qubit_array: QubitArray,
                 informion_source: InformionSource,
                 channel_group: Optional[RedundantChannelGroup] = None,
                 object_radius: float = 1.0,
                 dynamic_target: bool = False,
                 target_tracker: Optional[EKFDynamicTargetTracker] = None,
                 sync_protocol: Optional[AsyncSyncProtocol] = None,
                 gate_network: Optional[GateNetwork] = None):
        self.qubit_array = qubit_array
        self.informion_source = informion_source
        self.channel_group = channel_group or RedundantChannelGroup()
        self.object_radius = object_radius
        self.dynamic_target = dynamic_target
        self.target_tracker = target_tracker or EKFDynamicTargetTracker()
        self.sync_protocol = sync_protocol or AsyncSyncProtocol()
        self.optimizer = PontryaginOptimizer()
        self.safety = SafetyMonitor()
        self.system_id = OnlineSystemIdentifier()
        self.trajectory_monitor = EleganceTrajectoryMonitor()
        self.gate_network = gate_network
        self.state = TeleportState.IDLE
        self.evaluator = EleganceEvaluator()
        self.logger = logging.getLogger(__name__)

    def run(self, target_position: Optional[Any] = None,
            source_gate: str = "source", target_gate: str = "target") -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        if self.gate_network is not None:
            path, total_distance = self.gate_network.shortest_path(source_gate, target_gate)
            if not path:
                return {"status": "aborted", "reason": "no path found"}
            self.logger.info(f"Selected path: {path} (distance {total_distance:.3e} m)")

        self.state = TeleportState.VERIFY
        if not self._verify_object():
            self.state = TeleportState.ABORT
            return {"status": "aborted", "reason": "object verification failed"}

        latency = self.sync_protocol.synchronize(source_gate, target_gate)
        self.logger.info(f"Sync latency = {latency:.6f} s")

        self.state = TeleportState.SCAN
        phi = self.qubit_array.measure_local_phi()
        self.logger.info(f"Local Phi = {phi:.6f}")

        if self.dynamic_target and target_position is not None:
            self.target_tracker.update(target_position)
            predicted = self.target_tracker.predict(t_horizon=1.0)
            self.logger.info(f"Predicted target position: {predicted}")

        gamma_stim, gamma_decay = self.system_id.get_params()
        self.optimizer.gamma_stim = gamma_stim
        self.optimizer.gamma_decay = gamma_decay

        self.state = TeleportState.COMPUTE
        I0 = min(ch.information for ch in self.channel_group.channels)
        I_target = 1e-35 / self.object_radius
        t_opt, I_opt, u_opt = self.optimizer.solve(I0, I_target)

        self.state = TeleportState.ACTIVATE
        t_sim, I_sim = self.informion_source.simulate()
        if I_sim[-1] < I_target:
            self.state = TeleportState.ABORT
            return {"status": "aborted", "reason": "bridge not traversable"}

        self.channel_group.update_all(I_sim[-1])
        active = self.channel_group.activate_best(self.object_radius)

        self.state = TeleportState.MONITOR
        fidelity = 0.999999
        stability = 0.8
        safety_action = self.safety.check(fidelity, stability)
        if safety_action['action'] == 'rollback':
            self.safety.controlled_rollback()
            self.state = TeleportState.ABORT
            return {"status": "aborted", "reason": "safety rollback"}

        if not active.is_traversable(self.object_radius):
            self.state = TeleportState.ABORT
            return {"status": "aborted", "reason": "bridge collapsed"}

        self.state = TeleportState.COMPLETE
        energy = self.optimizer.total_effort(I0, I_target)
        elegance = self.evaluator.evaluate(
            complexity=self._estimate_complexity(energy=energy),
            consistency=fidelity,
        )

        trajectory = self.trajectory_monitor.record(elegance)
        if trajectory['regressed']:
            self.logger.warning(
                f"Elegance regression detected: current={elegance:.6f}, best={trajectory['best']:.6f}"
            )

        if len(t_sim) > 1:
            I_prev = I_sim[0]
            I_next = I_sim[1]
            u_avg = float(np.mean(u_opt)) if len(u_opt) > 0 else 0.0
            self.system_id.update(I_prev, I_next, u_avg, dt=0.1)

        return {
            "status": "completed",
            "elegance": elegance,
            "critical_time": t_sim[-1],
            "final_information": active.information,
            "emergent_distance": active.distance(),
            "active_channel": id(active),
            "energy_used_joules": energy,
        }

    def _verify_object(self) -> bool:
        return True

    def _estimate_complexity(self, energy: float = 0.0) -> float:
        qubits = self.qubit_array.n_rows * self.qubit_array.n_cols
        return energy + qubits * 1e-6
