# Surface Code Simulator

Rotated surface-code memory simulation with a Qiskit front end, optional Stim backend, and decoders (baseline local + PyMatching MWPM). This repository targets reproducible sweeps over physical error rates, code distances, and rounds, with deterministic seeding and CSV logs for every figure.

## Layout
- `src/surface_code_sim/` – Python package
  - `qiskit_frontend/` – circuit builders and Aer integration
  - `stim_backend/` – Stim export/run helpers
  - `decoders/` – baseline local decoder + PyMatching MWPM wiring
  - `utils/` – shared helpers (seeding, schemas)
- `experiments/` – run outputs (CSV logs)
- `figs/` – generated figures
- `tests/` – automated tests
- `notebooks/` – exploratory/demonstration notebooks

## Development quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
pytest
```

## Data model (step 2)
- Distances allowed: `3, 5, 7, 9`; decoders: `local` or `mwpm`; backends: `aer` or `stim`.
- Noise models:
  - `depolarizing`: fields `p` and readout flips `readout_error` (symmetric) or `readout_error_0to1`/`readout_error_1to0` (asymmetric).
  - `biased_pauli`: fields `px, py, pz` with optional asymmetric readout flips; sets `p=0`.
- Experiment configuration: `distance`, `rounds`, `shots`, `noise`, `decoder`, `backend`, `seed`. Validation is enforced in `ExperimentConfig`.
- RNG seeding: use `seed_everything(seed, salt=0)`; if `seed` is `None`, it reads `$SURFACE_CODE_SEED` or defaults to `0`.
- CSV schema (see `CSV_FIELDS`): `run_id, git_sha, seed, distance, rounds, shots, decoder, backend, p, px, py, pz, readout_error, readout_error_0to1, readout_error_1to0, logical_error_rate, ci_low, ci_high, wall_time_seconds, timestamp_utc`.
- CSV row helper: `make_csv_row` builds a canonical row from config + metadata.
- Figure command log format: use `FigureCommand.serialize()` to emit lines like `timestamp=... | figure=figs/distance3.png | seed=123 | cmd=python -m ... | notes=...`.
- Stim path: use `sample_syndromes_stim` for stim-based sampling; asymmetric readout error is not supported on the Stim path and will raise.
- CLI sweep: `python -m surface_code_sim.cli sweep --distance 3 --distance 5 --rounds 3 --shots 1000 --backend aer --decoder mwpm --p 0.001 --p 0.005 --seed 0 --jobs 1 --output experiments/runs.csv --git-sha $(git rev-parse --short HEAD)`. Run IDs are auto-prefixed; seeds increment per combination for determinism.
- Plotting: use `logical_error_curve` to render logical vs physical error with bootstrap CIs and `record_figure_command` to log figure provenance.
- Preset experiments: `python -m surface_code_sim.experiments.presets` runs depolarizing and biased sweeps (d=3,5,7,9) with Stim+MWPM, appends `experiments/presets.csv`, and writes figures to `figs/preset_dep.png` and `figs/preset_biased.png` with commands logged to `experiments/fig_commands.log`.
- Demo notebook: open `notebooks/qiskit_demo.ipynb` for a small Aer+local decoder example. Launch with `jupyter notebook` or VS Code.
- Profiling: `python -m surface_code_sim.profiling` times small Aer vs Stim runs.
- CSV outputs now include bootstrap CIs (ci_low/ci_high) and git_sha is resolved from the repo when available.

## Notes
- Dependencies are pinned for reproducibility. See `pyproject.toml` or `requirements*.txt`.
- Figures/logs are ignored by default; adjust `.gitignore` if you want to track specific artifacts.
