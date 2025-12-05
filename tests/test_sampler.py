import numpy as np

from surface_code_sim.qiskit_frontend import sample_syndromes
from surface_code_sim.utils import ExperimentConfig, NoiseParams


def test_sample_syndromes_zero_noise_has_no_detections():
    cfg = ExperimentConfig(
        distance=3,
        rounds=2,
        shots=4,
        noise=NoiseParams(model="depolarizing", p=0.0, readout_error=0.0),
        decoder="mwpm",
        backend="aer",
        seed=123,
    )
    synd = sample_syndromes(cfg)
    assert synd.x_detection.shape[0] == cfg.shots
    assert synd.z_detection.shape[0] == cfg.shots


def test_sample_syndromes_is_deterministic_with_seed():
    cfg = ExperimentConfig(
        distance=3,
        rounds=2,
        shots=5,
        noise=NoiseParams(model="depolarizing", p=0.05, readout_error=0.01),
        decoder="mwpm",
        backend="aer",
        seed=999,
    )
    synd1 = sample_syndromes(cfg)
    synd2 = sample_syndromes(cfg)
    assert np.array_equal(synd1.x_meas, synd2.x_meas)
    assert np.array_equal(synd1.z_meas, synd2.z_meas)
    assert np.array_equal(synd1.x_detection, synd2.x_detection)
    assert np.array_equal(synd1.z_detection, synd2.z_detection)
