import numpy as np
import stim

from surface_code_sim.qiskit_frontend import SampledSyndromes
from surface_code_sim.stim_backend.circuit import build_stim_memory_circuit
from surface_code_sim.utils import ExperimentConfig


def sample_syndromes_stim(config: ExperimentConfig) -> SampledSyndromes:
    circuit, x_count, z_count = build_stim_memory_circuit(config.distance, config.rounds, config.noise)
    sampler = circuit.compile_sampler(seed=config.seed)
    raw = sampler.sample(shots=config.shots)

    rounds = config.rounds
    z_meas = np.zeros((config.shots, rounds, z_count), dtype=np.uint8)
    x_meas = np.zeros((config.shots, rounds, x_count), dtype=np.uint8)

    for shot_idx, row in enumerate(raw):
        idx = 0
        for r in range(rounds):
            z_slice = row[idx : idx + z_count]
            z_meas[shot_idx, r, :] = z_slice
            idx += z_count
            x_slice = row[idx : idx + x_count]
            x_meas[shot_idx, r, :] = x_slice
            idx += x_count

    return SampledSyndromes(x_meas=x_meas, z_meas=z_meas)
