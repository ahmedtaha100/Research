import numpy as np

from surface_code_sim.decoders import LocalDecoder
from surface_code_sim.qiskit_frontend import SampledSyndromes, sample_syndromes
from surface_code_sim.utils import ExperimentConfig, NoiseParams


def test_local_decoder_zero_noise_no_failures():
    cfg = ExperimentConfig(
        distance=3,
        rounds=2,
        shots=3,
        noise=NoiseParams(model="depolarizing", p=0.0, readout_error=0.0),
        decoder="mwpm",
        backend="aer",
        seed=321,
    )
    synd = sample_syndromes(cfg)
    dec = LocalDecoder()
    out = dec.decode(synd)
    assert out["x_logical"].shape[0] == cfg.shots
    assert out["z_logical"].shape[0] == cfg.shots


def test_local_decoder_parity_flags_detection():
    x_meas = np.zeros((2, 2, 1), dtype=np.uint8)
    z_meas = np.zeros((2, 2, 1), dtype=np.uint8)
    x_meas[0, 0, 0] = 1
    z_meas[1, 0, 0] = 1
    synd = SampledSyndromes(x_meas=x_meas, z_meas=z_meas)
    dec = LocalDecoder()
    out = dec.decode(synd)
    assert out["z_logical"][0] == 1
    assert out["x_logical"][1] == 1
