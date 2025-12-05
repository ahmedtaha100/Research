import pytest

from surface_code_sim.utils import (
    ALLOWED_BACKENDS,
    ALLOWED_DECODERS,
    ALLOWED_DISTANCES,
    ExperimentConfig,
    FigureCommand,
    NoiseParams,
    RunMetadata,
    make_csv_row,
)


def test_noise_params_validate_depolarizing():
    noise = NoiseParams(model="depolarizing", p=0.01, readout_error=0.02)
    noise.validate()
    assert noise.p == 0.01
    assert noise.px is None


def test_noise_params_validate_biased_pauli():
    noise = NoiseParams(model="biased_pauli", px=0.01, py=0.02, pz=0.03)
    noise.validate()
    assert noise.p == 0.0


def test_noise_params_validate_asymmetric_readout():
    noise = NoiseParams(model="depolarizing", p=0.0, readout_error_0to1=0.1, readout_error_1to0=0.2)
    noise.validate()


def test_experiment_config_validates_and_to_dict():
    noise = NoiseParams(model="depolarizing", p=0.001)
    cfg = ExperimentConfig(distance=3, rounds=2, shots=100, noise=noise, decoder="mwpm", backend="aer", seed=42)
    as_dict = cfg.to_dict()
    assert as_dict["distance"] == 3
    assert as_dict["p"] == 0.001
    assert as_dict["readout_error"] == 0.0


@pytest.mark.parametrize("distance", [1, 2, 4])
def test_experiment_config_invalid_distance(distance):
    noise = NoiseParams(model="depolarizing", p=0.001)
    with pytest.raises(ValueError):
        ExperimentConfig(distance=distance, rounds=2, shots=100, noise=noise)


def test_make_csv_row_fields_complete():
    noise = NoiseParams(model="depolarizing", p=0.01, readout_error=0.02)
    cfg = ExperimentConfig(distance=5, rounds=3, shots=200, noise=noise, decoder=ALLOWED_DECODERS[0], backend=ALLOWED_BACKENDS[0], seed=7)
    meta = RunMetadata(run_id="run-001", git_sha="abc123", command="cli --demo", seed=7)
    row = make_csv_row(metadata=meta, config=cfg, logical_error_rate=0.1, ci_low=0.08, ci_high=0.12, wall_time_seconds=1.5)
    for key in ("run_id", "git_sha", "seed", "distance", "rounds", "shots", "decoder", "backend", "p", "readout_error", "readout_error_0to1", "readout_error_1to0", "logical_error_rate", "ci_low", "ci_high", "wall_time_seconds", "timestamp_utc"):
        assert key in row


def test_figure_command_serialization():
    entry = FigureCommand(figure_path="figs/demo.png", command="plot --input x.csv", seed=5, notes="test")
    line = entry.serialize()
    assert "figs/demo.png" in line
    assert "seed=5" in line
