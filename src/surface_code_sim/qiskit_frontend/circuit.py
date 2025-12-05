from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from surface_code_sim.qiskit_frontend.layout import RotatedCodeLayout, build_layout


def build_memory_circuit(distance: int, rounds: int) -> tuple[QuantumCircuit, RotatedCodeLayout]:
    if rounds <= 0:
        raise ValueError("rounds must be positive")

    layout = build_layout(distance)

    data = QuantumRegister(len(layout.data_indices), "data")
    x_anc = QuantumRegister(len(layout.x_stabilizers), "x_anc")
    z_anc = QuantumRegister(len(layout.z_stabilizers), "z_anc")

    x_cl = ClassicalRegister(rounds * len(layout.x_stabilizers), "mx")
    z_cl = ClassicalRegister(rounds * len(layout.z_stabilizers), "mz")

    circuit = QuantumCircuit(data, x_anc, z_anc, x_cl, z_cl, name=f"surface_code_d{distance}")

    for r in range(rounds):
        for anc_idx, qubits in enumerate(layout.z_stabilizers):
            circuit.reset(z_anc[anc_idx])
            for data_idx in qubits:
                circuit.cx(data[data_idx], z_anc[anc_idx])
            cbit = r * len(layout.z_stabilizers) + anc_idx
            circuit.measure(z_anc[anc_idx], z_cl[cbit])

        for anc_idx, qubits in enumerate(layout.x_stabilizers):
            circuit.reset(x_anc[anc_idx])
            circuit.h(x_anc[anc_idx])
            for data_idx in qubits:
                circuit.cx(x_anc[anc_idx], data[data_idx])
            circuit.h(x_anc[anc_idx])
            cbit = r * len(layout.x_stabilizers) + anc_idx
            circuit.measure(x_anc[anc_idx], x_cl[cbit])

    return circuit, layout
