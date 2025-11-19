#!/usr/bin/env python3
"""
QRL Traffic Risk Agent
Quantum-inspired policy for traffic risk classification.

This module does NOT replace your traffic forecasting model.
It sits on top of the FGCUTrafficForecaster and maps
(predicted volume, hour) -> discrete risk level.
"""

from typing import Dict
import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

# Four discrete risk levels / intervention categories
ACTIONS = ["NORMAL", "WATCH", "CONGESTED", "CRITICAL"]


class QRLTrafficAgent:
    """
    Quantum Reinforcement Learning style agent that maps
    simple traffic features to a discrete risk label.

    State: [normalized_volume, normalized_hour]
    Output: probabilities over 4 risk levels (ACTIONS).
    """

    def __init__(self, n_qubits: int = 2, n_layers: int = 2, seed: int = 42):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.rng = np.random.default_rng(seed)

        # Quantum device (simulator)
        self.dev = qml.device("default.qubit", wires=self.n_qubits)

        # Initialize variational circuit weights
        # shape: (layers, qubits, 3) for RX, RY, RZ per qubit
        init = self.rng.normal(loc=0.0, scale=0.1, size=(n_layers, n_qubits, 3))
        self.weights = pnp.array(init, requires_grad=True)

        self._build_qnode()

    def _build_qnode(self):
        dev = self.dev
        n_qubits = self.n_qubits
        n_layers = self.n_layers

        @qml.qnode(dev)
        def policy_circuit(x, weights):
            """
            Quantum policy circuit.

            x: 2D input [norm_volume, norm_hour]
            weights: PQC parameters of shape (layers, n_qubits, 3)
            """
            # Simple angle encoding on first 2 qubits
            qml.RY(np.pi * x[0], wires=0)
            if n_qubits > 1:
                qml.RY(np.pi * x[1], wires=1)

            # Variational layers
            for l in range(n_layers):
                # Entanglement
                if n_qubits > 1:
                    qml.CNOT(wires=[0, 1])
                # Local rotations
                for q in range(n_qubits):
                    rx, ry, rz = weights[l, q]
                    qml.RX(rx, wires=q)
                    qml.RY(ry, wires=q)
                    qml.RZ(rz, wires=q)

            # Measure probabilities of computational basis states
            return qml.probs(wires=list(range(n_qubits)))

        self.policy_circuit = policy_circuit

    def _action_probs(self, state_vec: np.ndarray) -> pnp.ndarray:
        """
        Map state_vec -> probabilities over 4 actions.
        For 2 qubits, we have 4 basis states |00>,|01>,|10>,|11|.
        """
        probs = self.policy_circuit(state_vec, self.weights)
        # Ensure shape (4,)
        if probs.shape[0] < 4:
            probs = pnp.pad(probs, (0, 4 - probs.shape[0]))
        probs = probs / pnp.sum(probs)
        return probs

    def classify_risk(self, volume: float, hour: int) -> Dict:
        """
        Public API: classify traffic risk from predicted volume + hour.

        volume: predicted vehicles/hour (e.g., from FGCUTrafficForecaster)
        hour: 0-23 (local time)

        Returns:
            {
              "risk_label": str,
              "action_index": int,
              "probs": { "NORMAL": p0, "WATCH": p1, ... }
            }
        """
        # Normalize volume (assuming upper bound ~800 from your model)
        norm_vol = float(np.clip(volume / 800.0, 0.0, 1.0))
        norm_hour = float(np.clip(hour / 23.0, 0.0, 1.0))

        state_vec = pnp.array([norm_vol, norm_hour], requires_grad=False)
        probs = self._action_probs(state_vec)
        probs_np = np.array(probs, dtype=float)

        # Greedy action selection for now (you can change to sampling later)
        action_idx = int(np.argmax(probs_np))
        risk_label = ACTIONS[action_idx]

        return {
            "risk_label": risk_label,
            "action_index": action_idx,
            "probs": {label: float(p) for label, p in zip(ACTIONS, probs_np)},
        }


if __name__ == "__main__":
    # Quick local test
    agent = QRLTrafficAgent()
    test = agent.classify_risk(volume=450, hour=17)
    print(test)
