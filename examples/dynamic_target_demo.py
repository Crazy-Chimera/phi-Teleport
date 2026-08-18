#!/usr/bin/env python3
"""
Dynamic target teleportation example.

Simulates a target moving along a trajectory, uses the EKF tracker
to predict its position, and runs the controller in dynamic mode.
"""

import numpy as np
import logging
from phi_teleport.quantum.qubit_array import QubitArray
from phi_teleport.quantum.informion_source import InformionSource
from phi_teleport.control.teleportation_controller import TeleportationController
from phi_teleport.quantum.dynamic_target_ekf import EKFDynamicTargetTracker

logging.basicConfig(level=logging.INFO)

def main():
    print("Φ‑Teleport Dynamic Target Example")
    print("=" * 50)

    # Create a larger qubit array.
    qubits = QubitArray(rows=8, cols=8)
    source = InformionSource(gamma_stim=0.3, gamma_dec=0.01)

    # Create an EKF tracker for the dynamic target.
    tracker = EKFDynamicTargetTracker(dt=0.1)

    # Simulate target motion: circular trajectory.
    positions = []
    for i in range(50):
        t = i * 0.1
        x = 5.0 * np.cos(t)
        y = 5.0 * np.sin(t)
        z = 0.0
        positions.append([x, y, z])
        tracker.update([x, y, z])

    # Get the last known position and predicted future position.
    last_pos = positions[-1]
    predicted = tracker.predict(t_horizon=1.0)

    print(f"Last known target position: {last_pos}")
    print(f"Predicted position (1s ahead): {predicted}")

    # Run the controller in dynamic mode.
    controller = TeleportationController(
        qubit_array=qubits,
        informion_source=source,
        dynamic_target=True,
        target_tracker=tracker,
    )
    result = controller.run(target_position=predicted)

    print(f"\nStatus: {result['status']}")
    print(f"Elegance: {result['elegance']:.6f}")

if __name__ == '__main__':
    main()
