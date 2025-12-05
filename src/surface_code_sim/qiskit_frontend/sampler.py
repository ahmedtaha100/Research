import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from surface_code_sim.qiskit_frontend import build_layout, build_memory_circuit, build_noise_model
from surface_code_sim.utils import ExperimentConfig, seed_everything


class SampledSyndromes:
    def __init__(self, x_meas: np.ndarray, z_meas: np.ndarray):
        self.x_meas = x_meas
        self.z_meas = z_meas
        self.x_detection = self._detection_events(self.x_meas)
        self.z_detection = self._detection_events(self.z_meas)

    @staticmethod
    def _detection_events(meas: np.ndarray) -> np.ndarray:
        detection = np.zeros_like(meas, dtype=np.uint8)
        detection[:, 0, :] = meas[:, 0, :]
        if meas.shape[1] > 1:
            detection[:, 1:, :] = np.bitwise_xor(meas[:, 1:, :], meas[:, :-1, :])
        return detection


def sample_syndromes(config: ExperimentConfig) -> SampledSyndromes:
    seed_info = seed_everything(config.seed)
    circuit, layout = build_memory_circuit(config.distance, config.rounds)
    noise_model = build_noise_model(config.noise)
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=seed_info["seed"])
    transpiled = transpile(circuit, simulator, optimization_level=0)
    result = simulator.run(transpiled, shots=config.shots, memory=True).result()
    memory = result.get_memory(transpiled)

    x_count = len(layout.x_stabilizers)
    z_count = len(layout.z_stabilizers)
    rounds = config.rounds

    x_meas = np.zeros((config.shots, rounds, x_count), dtype=np.uint8)
    z_meas = np.zeros((config.shots, rounds, z_count), dtype=np.uint8)

    for shot_idx, bitstring in enumerate(memory):
        cleaned = bitstring.replace(" ", "")
        bits = np.fromiter((int(b) for b in cleaned[::-1]), dtype=np.uint8)
        x_bits = bits[: rounds * x_count].reshape(rounds, x_count)
        z_bits = bits[rounds * x_count : rounds * x_count + rounds * z_count].reshape(rounds, z_count)
        x_meas[shot_idx] = x_bits
        z_meas[shot_idx] = z_bits

    return SampledSyndromes(x_meas=x_meas, z_meas=z_meas)
