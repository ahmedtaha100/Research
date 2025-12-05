import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path
from typing import Iterable

import pandas as pd
import typer

from surface_code_sim.decoders import LocalDecoder, MwpmDecoder
from surface_code_sim.qiskit_frontend import SampledSyndromes, sample_syndromes
from surface_code_sim.stim_backend import sample_syndromes_stim
from surface_code_sim.utils import (
    ALLOWED_BACKENDS,
    ALLOWED_DECODERS,
    ExperimentConfig,
    NoiseParams,
    RunMetadata,
    make_csv_row,
    resolve_git_sha,
)
from surface_code_sim.plotting import bootstrap_ci

app = typer.Typer(add_completion=False)


def _decoder_factory(name: str, distance: int):
    if name == "local":
        return LocalDecoder()
    if name == "mwpm":
        return MwpmDecoder.from_distance(distance)
    raise ValueError(f"Unknown decoder {name}")


def _sample(config: ExperimentConfig) -> SampledSyndromes:
    if config.backend == "aer":
        return sample_syndromes(config)
    if config.backend == "stim":
        return sample_syndromes_stim(config)
    raise ValueError(f"Unknown backend {config.backend}")


def _run_once(cfg: ExperimentConfig, git_sha: str, run_id: str) -> dict:
    start = time.time()
    syndromes = _sample(cfg)
    decoder_instance = _decoder_factory(cfg.decoder, cfg.distance)
    decoded = decoder_instance.decode(syndromes)
    wall = time.time() - start
    logical_errors = ((decoded["x_logical"] | decoded["z_logical"]) != 0).astype(int)
    logical_error_rate = float(logical_errors.mean())
    ci_low, ci_high = bootstrap_ci(logical_errors, num_samples=1000, alpha=0.05, seed=cfg.seed) if len(logical_errors) > 1 else (None, None)
    meta = RunMetadata(run_id=run_id, git_sha=git_sha, command="cli sweep", seed=cfg.seed)
    return make_csv_row(
        metadata=meta,
        config=cfg,
        logical_error_rate=logical_error_rate,
        ci_low=ci_low,
        ci_high=ci_high,
        wall_time_seconds=wall,
    )


def _noise_model(px: float | None, py: float | None, pz: float | None) -> str:
    return "biased_pauli" if any(v is not None for v in (px, py, pz)) else "depolarizing"


def _sweep_configs(
    distances: Iterable[int],
    p_values: Iterable[float],
    backends: Iterable[str],
    decoders: Iterable[str],
    rounds: int,
    shots: int,
    px: float | None,
    py: float | None,
    pz: float | None,
    readout_error: float,
    readout_error_0to1: float | None,
    readout_error_1to0: float | None,
    base_seed: int,
) -> list[ExperimentConfig]:
    configs: list[ExperimentConfig] = []
    noise_model = _noise_model(px, py, pz)
    seed_offset = 0
    for distance, backend, decoder, p_val in product(distances, backends, decoders, p_values):
        noise = NoiseParams(
            model=noise_model,
            p=p_val,
            px=px,
            py=py,
            pz=pz,
            readout_error=readout_error,
            readout_error_0to1=readout_error_0to1,
            readout_error_1to0=readout_error_1to0,
        )
        cfg = ExperimentConfig(
            distance=distance,
            rounds=rounds,
            shots=shots,
            noise=noise,
            decoder=decoder,
            backend=backend,
            seed=base_seed + seed_offset,
        )
        configs.append(cfg)
        seed_offset += 1
    return configs


def run_sweep(
    distance: list[int],
    rounds: int,
    shots: int,
    backend: list[str],
    decoder: list[str],
    p: list[float],
    px: float | None = None,
    py: float | None = None,
    pz: float | None = None,
    readout_error: float = 0.0,
    readout_error_0to1: float | None = None,
    readout_error_1to0: float | None = None,
    seed: int = 0,
    jobs: int = 1,
    output: Path = Path("experiments") / "runs.csv",
    git_sha: str | None = None,
    run_prefix: str | None = None,
):
    git_sha = git_sha or resolve_git_sha()
    run_prefix = run_prefix or f"run-{uuid.uuid4().hex[:6]}"
    configs = _sweep_configs(
        distances=distance,
        p_values=p,
        backends=backend,
        decoders=decoder,
        rounds=rounds,
        shots=shots,
        px=px,
        py=py,
        pz=pz,
        readout_error=readout_error,
        readout_error_0to1=readout_error_0to1,
        readout_error_1to0=readout_error_1to0,
        base_seed=seed,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    if jobs == 1:
        for idx, cfg in enumerate(configs):
            run_id = f"{run_prefix}-{idx:04d}"
            rows.append(_run_once(cfg, git_sha, run_id))
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = []
            for idx, cfg in enumerate(configs):
                run_id = f"{run_prefix}-{idx:04d}"
                futures.append(pool.submit(_run_once, cfg, git_sha, run_id))
            for fut in futures:
                rows.append(fut.result())
    df = pd.DataFrame(rows)
    header = not output.exists()
    df.to_csv(output, mode="a", header=header, index=False)
    typer.echo(f"Wrote {len(rows)} rows to {output}")


@app.command()
def sweep(
    distance: list[int] = typer.Option([3], "-d", "--distance", help="Code distance; can repeat for sweep"),
    rounds: int = typer.Option(..., help="Number of stabilizer measurement rounds"),
    shots: int = typer.Option(..., help="Number of shots"),
    backend: list[str] = typer.Option(["aer"], help=f"Backend: {ALLOWED_BACKENDS}"),
    decoder: list[str] = typer.Option(["mwpm"], help=f"Decoder: {ALLOWED_DECODERS}"),
    p: list[float] = typer.Option([0.0], help="Depolarizing probability p; can repeat"),
    px: float = typer.Option(None, help="Biased Pauli px"),
    py: float = typer.Option(None, help="Biased Pauli py"),
    pz: float = typer.Option(None, help="Biased Pauli pz"),
    readout_error: float = typer.Option(0.0, help="Symmetric readout flip probability"),
    readout_error_0to1: float = typer.Option(None, help="Asymmetric readout flip 0->1"),
    readout_error_1to0: float = typer.Option(None, help="Asymmetric readout flip 1->0"),
    seed: int = typer.Option(0, help="Base seed"),
    jobs: int = typer.Option(1, help="Parallel workers"),
    output: Path = typer.Option(Path("experiments") / "runs.csv", help="CSV output path"),
    git_sha: str = typer.Option("unknown", help="Git short SHA for provenance"),
    run_prefix: str = typer.Option(None, help="Prefix for run_id values"),
):
    run_sweep(
        distance=distance,
        rounds=rounds,
        shots=shots,
        backend=backend,
        decoder=decoder,
        p=p,
        px=px,
        py=py,
        pz=pz,
        readout_error=readout_error,
        readout_error_0to1=readout_error_0to1,
        readout_error_1to0=readout_error_1to0,
        seed=seed,
        jobs=jobs,
        output=output,
        git_sha=git_sha,
        run_prefix=run_prefix,
    )


def main():
    app()


if __name__ == "__main__":
    main()
