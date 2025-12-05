# Surface Code Simulator

Rotated surface-code memory simulator with Qiskit/Aer and Stim backends, plus local and MWPM decoders. Runs preset sweeps and writes CSVs/figures for quick logical-error checks.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pytest
```

Run presets (Stim + MWPM):
```bash
python -m surface_code_sim.experiments.presets
```

CLI sweeps (example):
```bash
python -m surface_code_sim.cli sweep --distance 3 --rounds 3 --shots 500 --backend stim --decoder mwpm --p 0.001 --output experiments/runs.csv
```
