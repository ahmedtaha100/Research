import pandas as pd

from surface_code_sim.cli import run_sweep


def test_cli_sweep_writes_csv(tmp_path, monkeypatch):
    out = tmp_path / "runs.csv"
    args = dict(
        distance=[3],
        rounds=1,
        shots=2,
        backend=["stim"],
        decoder=["local"],
        p=[0.0],
        seed=0,
        jobs=1,
        output=out,
        git_sha="abc",
        run_prefix="test",
    )
    run_sweep(**args)
    df = pd.read_csv(out)
    assert len(df) == 1
    assert df.iloc[0]["run_id"] == "test-0000"
