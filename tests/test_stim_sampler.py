import numpy as np
import pytest

from surface_code_sim.stim_backend import sample_syndromes_stim
from surface_code_sim.utils import ExperimentConfig, NoiseParams


def test_stim_syndromes_zero_noise_no_detections():
    cfg = ExperimentConfig(
        distance=3,
        rounds=2,
        shots=4,
        noise=NoiseParams(model="depolarizing", p=0.0, readout_error=0.0),
        decoder="mwpm",
        backend="stim",
        seed=111,
    )
    synd = sample_syndromes_stim(cfg)
    assert synd.x_detection.shape[0] == cfg.shots
    assert synd.z_detection.shape[0] == cfg.shots


def test_stim_syndromes_deterministic_with_seed():
    cfg = ExperimentConfig(
        distance=3,
        rounds=2,
        shots=5,
        noise=NoiseParams(model="depolarizing", p=0.02, readout_error=0.01),
        decoder="mwpm",
        backend="stim",
        seed=222,
    )
    s1 = sample_syndromes_stim(cfg)
    s2 = sample_syndromes_stim(cfg)
    assert np.array_equal(s1.x_meas, s2.x_meas)
    assert np.array_equal(s1.z_meas, s2.z_meas)


def test_stim_syndromes_rejects_asymmetric_readout():
    cfg = ExperimentConfig(
        distance=3,
        rounds=1,
        shots=1,
        noise=NoiseParams(model="depolarizing", p=0.0, readout_error_0to1=0.1, readout_error_1to0=0.2),
        decoder="mwpm",
        backend="stim",
        seed=1,
    )
    with pytest.raises(ValueError):
        sample_syndromes_stim(cfg)
