from dataclasses import dataclass

from surface_code_sim.utils import ALLOWED_DISTANCES


@dataclass(frozen=True)
class RotatedCodeLayout:
    distance: int
    data_indices: list[int]
    x_stabilizers: list[list[int]]
    z_stabilizers: list[list[int]]


def build_layout(distance: int) -> RotatedCodeLayout:
    if distance not in ALLOWED_DISTANCES:
        raise ValueError(f"distance must be one of {ALLOWED_DISTANCES}")

    data_indices = list(range(distance * distance))
    x_stabilizers: list[list[int]] = []
    z_stabilizers: list[list[int]] = []

    for row in range(distance - 1):
        for col in range(distance - 1):
            d0 = row * distance + col
            d1 = (row + 1) * distance + col
            d2 = row * distance + (col + 1)
            d3 = (row + 1) * distance + (col + 1)
            qubits = [d0, d1, d2, d3]
            if (row + col) % 2 == 0:
                x_stabilizers.append(qubits)
            else:
                z_stabilizers.append(qubits)

    return RotatedCodeLayout(
        distance=distance,
        data_indices=data_indices,
        x_stabilizers=x_stabilizers,
        z_stabilizers=z_stabilizers,
    )
