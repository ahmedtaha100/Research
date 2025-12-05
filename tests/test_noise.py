import pytest

from surface_code_sim.qiskit_frontend import build_noise_model
from surface_code_sim.utils import NoiseParams


def test_depolarizing_noise_model_includes_ops_and_readout():
    noise = NoiseParams(model="depolarizing", p=0.1, readout_error=0.05)
    model = build_noise_model(noise)
    data = model.to_dict()
    ops = {op for err in data["errors"] for op in err.get("operations", [])}
    assert "cx" in ops
    assert "h" in ops
    assert model._default_readout_error is not None
    probs = model._default_readout_error.probabilities
    assert probs.shape == (2, 2)
    assert abs(probs[0][1] - 0.05) < 1e-9


def test_biased_pauli_noise_model_and_asymmetric_readout():
    noise = NoiseParams(model="biased_pauli", px=0.1, py=0.0, pz=0.2, readout_error_0to1=0.1, readout_error_1to0=0.3)
    model = build_noise_model(noise)
    data = model.to_dict()
    h_err = next(err for err in data["errors"] if "h" in err.get("operations", []))
    assert abs(sum(h_err["probabilities"]) - 1.0) < 1e-9
    probs = model._default_readout_error.probabilities
    assert probs.shape == (2, 2)
    assert abs(probs[0][1] - 0.1) < 1e-9
    assert abs(probs[1][0] - 0.3) < 1e-9


def test_biased_pauli_invalid_sum_raises():
    with pytest.raises(ValueError):
        NoiseParams(model="biased_pauli", px=0.6, py=0.3, pz=0.2).validate()
