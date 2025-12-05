from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error, pauli_error

from surface_code_sim.utils import NoiseParams


def _readout_matrix(noise: NoiseParams) -> list[list[float]]:
    if noise.readout_error_0to1 is not None:
        p01 = noise.readout_error_0to1
        p10 = noise.readout_error_1to0
    else:
        p01 = noise.readout_error
        p10 = noise.readout_error
    return [[1 - p01, p01], [p10, 1 - p10]]


def build_noise_model(noise: NoiseParams) -> NoiseModel:
    noise.validate()
    model = NoiseModel()

    if noise.model == "depolarizing":
        single = depolarizing_error(noise.p, 1)
        two = depolarizing_error(noise.p, 2)
    else:
        i_prob = 1 - (float(noise.px) + float(noise.py) + float(noise.pz))
        single = pauli_error(
            [
                ("X", float(noise.px)),
                ("Y", float(noise.py)),
                ("Z", float(noise.pz)),
                ("I", i_prob),
            ]
        )
        two = single.tensor(single)

    one_qubit_ops = ["h", "id", "reset"]
    two_qubit_ops = ["cx"]

    model.add_all_qubit_quantum_error(single, one_qubit_ops)
    model.add_all_qubit_quantum_error(two, two_qubit_ops)

    readout = ReadoutError(_readout_matrix(noise))
    model.add_all_qubit_readout_error(readout)
    return model
