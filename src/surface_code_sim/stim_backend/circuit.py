import stim

from surface_code_sim.qiskit_frontend import build_layout
from surface_code_sim.utils import NoiseParams


def _single_qubit_noise(circuit: stim.Circuit, qubit: int, noise: NoiseParams) -> None:
    if noise.model == "depolarizing":
        if noise.p > 0:
            circuit.append("DEPOLARIZE1", [qubit], noise.p)
    else:
        circuit.append("PAULI_CHANNEL_1", [qubit], [float(noise.px), float(noise.py), float(noise.pz)])


def _two_qubit_noise(circuit: stim.Circuit, q0: int, q1: int, noise: NoiseParams) -> None:
    if noise.model == "depolarizing":
        if noise.p > 0:
            circuit.append("DEPOLARIZE2", [q0, q1], noise.p)
    else:
        _single_qubit_noise(circuit, q0, noise)
        _single_qubit_noise(circuit, q1, noise)


def build_stim_memory_circuit(distance: int, rounds: int, noise: NoiseParams) -> tuple[stim.Circuit, int, int]:
    noise.validate()
    if noise.readout_error_0to1 is not None and noise.readout_error_0to1 != noise.readout_error_1to0:
        raise ValueError("Asymmetric readout error not supported in Stim path")
    readout_p = noise.readout_error_0to1 if noise.readout_error_0to1 is not None else noise.readout_error

    layout = build_layout(distance)
    data_count = len(layout.data_indices)
    z_count = len(layout.z_stabilizers)
    x_count = len(layout.x_stabilizers)

    circuit = stim.Circuit()
    for _ in range(rounds):
        for anc_idx, stab in enumerate(layout.z_stabilizers):
            anc = data_count + anc_idx
            circuit.append("R", [anc])
            for data_idx in stab:
                circuit.append("CX", [data_idx, anc])
                _two_qubit_noise(circuit, data_idx, anc, noise)
            if readout_p > 0:
                circuit.append("X_ERROR", [anc], readout_p)
            circuit.append("M", [anc])
        for anc_idx, stab in enumerate(layout.x_stabilizers):
            anc = data_count + z_count + anc_idx
            circuit.append("R", [anc])
            circuit.append("H", [anc])
            _single_qubit_noise(circuit, anc, noise)
            for data_idx in stab:
                circuit.append("CX", [anc, data_idx])
                _two_qubit_noise(circuit, anc, data_idx, noise)
            circuit.append("H", [anc])
            _single_qubit_noise(circuit, anc, noise)
            if readout_p > 0:
                circuit.append("X_ERROR", [anc], readout_p)
            circuit.append("M", [anc])
    return circuit, x_count, z_count
