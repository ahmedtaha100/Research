from datetime import datetime
from pathlib import Path

import pandas as pd

from surface_code_sim.cli import _run_once, _sweep_configs
from surface_code_sim.plotting import logical_error_curve, record_figure_command
from surface_code_sim.utils import resolve_git_sha


def run_presets():
    git_sha = resolve_git_sha()
    prefix = f"preset-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cmd_log = Path("experiments/run_commands.log")
    cmd_log.parent.mkdir(parents=True, exist_ok=True)
    with cmd_log.open("a") as f:
        f.write(f"{datetime.now().isoformat()} python -m surface_code_sim.experiments.presets\n")
    dep_configs = _sweep_configs(
        distances=[3, 5, 7, 9],
        p_values=[0.001, 0.002, 0.005, 0.01],
        backends=["stim"],
        decoders=["mwpm"],
        rounds=3,
        shots=200,
        px=None,
        py=None,
        pz=None,
        readout_error=0.01,
        readout_error_0to1=None,
        readout_error_1to0=None,
        base_seed=0,
    )
    biased_configs = _sweep_configs(
        distances=[3, 5, 7, 9],
        p_values=[0.0],
        backends=["stim"],
        decoders=["mwpm"],
        rounds=3,
        shots=200,
        px=0.05,
        py=0.0,
        pz=0.15,
        readout_error=0.01,
        readout_error_0to1=None,
        readout_error_1to0=None,
        base_seed=1000,
    )
    rows = []
    for idx, cfg in enumerate(dep_configs + biased_configs):
        run_id = f"{prefix}-{idx:04d}"
        rows.append(_run_once(cfg, git_sha, run_id))
    df = pd.DataFrame(rows)
    output = Path("experiments/presets.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    header = not output.exists()
    df.to_csv(output, mode="a", header=header, index=False)
    dep_df = df[df["px"].isna()]
    biased_df = df[df["px"].notna()]
    figs_dir = Path("figs")
    logical_error_curve(dep_df, distances=[3, 5, 7, 9], output=figs_dir / "preset_dep.png", title="Depolarizing presets", seed=0)
    logical_error_curve(biased_df, distances=[3, 5, 7, 9], output=figs_dir / "preset_biased.png", title="Biased presets", seed=0)
    record_figure_command(figs_dir / "preset_dep.png", "python -m surface_code_sim.experiments.presets", 0, Path("experiments/fig_commands.log"), notes="dep presets")
    record_figure_command(figs_dir / "preset_biased.png", "python -m surface_code_sim.experiments.presets", 0, Path("experiments/fig_commands.log"), notes="biased presets")


if __name__ == "__main__":
    run_presets()
