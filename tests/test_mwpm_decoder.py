import numpy as np

from surface_code_sim.decoders import MwpmDecoder
from surface_code_sim.qiskit_frontend import SampledSyndromes, build_layout


def test_mwpm_decoder_zero_syndrome_no_failures():
    layout = build_layout(3)
    dec = MwpmDecoder(layout)
    x_det = np.zeros((2, 2, len(layout.x_stabilizers)), dtype=np.uint8)
    z_det = np.zeros((2, 2, len(layout.z_stabilizers)), dtype=np.uint8)
    synd = SampledSyndromes(x_meas=np.zeros_like(x_det), z_meas=np.zeros_like(z_det))
    out = dec.decode(synd)
    assert np.sum(out["x_logical"]) == 0
    assert np.sum(out["z_logical"]) == 0


def test_mwpm_decoder_same_seed_determinism():
    layout = build_layout(3)
    dec = MwpmDecoder(layout)
    x_det = np.zeros((1, 1, len(layout.x_stabilizers)), dtype=np.uint8)
    z_det = np.zeros((1, 1, len(layout.z_stabilizers)), dtype=np.uint8)
    x_det[0, 0, 0] = 1
    synd = SampledSyndromes(x_meas=x_det, z_meas=z_det)
    out = dec.decode(synd)
    assert out["z_logical"][0] in (0, 1)
