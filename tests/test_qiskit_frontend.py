import pytest

from surface_code_sim.qiskit_frontend import build_layout, build_memory_circuit


def test_layout_counts_distance3():
    layout = build_layout(3)
    assert len(layout.data_indices) == 9
    assert len(layout.x_stabilizers) == 2
    assert len(layout.z_stabilizers) == 2
    for stab in layout.x_stabilizers + layout.z_stabilizers:
        assert len(stab) == 4


def test_layout_counts_distance5():
    layout = build_layout(5)
    assert len(layout.data_indices) == 25
    assert len(layout.x_stabilizers) == 8
    assert len(layout.z_stabilizers) == 8


def test_build_memory_circuit_register_sizes():
    rounds = 3
    circuit, layout = build_memory_circuit(5, rounds)
    expected_qubits = len(layout.data_indices) + len(layout.x_stabilizers) + len(layout.z_stabilizers)
    expected_clbits = rounds * (len(layout.x_stabilizers) + len(layout.z_stabilizers))
    assert circuit.num_qubits == expected_qubits
    assert circuit.num_clbits == expected_clbits


def test_build_memory_circuit_measurements_match_rounds():
    rounds = 2
    circuit, layout = build_memory_circuit(3, rounds)
    measurements = [inst for inst, _, _ in circuit.data if inst.name == "measure"]
    assert len(measurements) == rounds * (len(layout.x_stabilizers) + len(layout.z_stabilizers))


def test_invalid_distance_raises():
    with pytest.raises(ValueError):
        build_layout(4)


def test_invalid_rounds_raises():
    with pytest.raises(ValueError):
        build_memory_circuit(3, 0)
