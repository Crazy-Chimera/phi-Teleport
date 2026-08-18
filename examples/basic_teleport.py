#!/usr/bin/env python3
"""
Basic teleportation example.

Creates a small qubit array and informion source, then runs the
teleportation controller and prints the elegance score.
"""

import logging
from phi_teleport.quantum.qubit_array import QubitArray
from phi_teleport.quantum.informion_source import InformionSource
from phi_teleport.control.teleportation_controller import TeleportationController

logging.basicConfig(level=logging.INFO)

def main():
    print("Φ‑Teleport Basic Example")
    print("=" * 50)

    # Create a small qubit array (4x4) for demonstration.
    qubits = QubitArray(rows=4, cols=4)

    # Create an informion source with strong stimulated emission.
    source = InformionSource(gamma_stim=0.3, gamma_dec=0.01)

    # Create the controller.
    controller = TeleportationController(qubit_array=qubits, informion_source=source)

    # Run the teleportation.
    result = controller.run()

    print(f"Status: {result['status']}")
    print(f"Elegance (C/K): {result['elegance']:.6f}")
    print(f"Final mutual information: {result['final_information']:.3e}")
    print(f"Emergent distance: {result['emergent_distance']:.3e} m")
    print(f"Energy used: {result['energy_used_joules']:.3e} J")

if __name__ == '__main__':
    main()
