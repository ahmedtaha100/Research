import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def bootstrap_ci(data: np.ndarray, num_samples: int = 5000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    samples = rng.choice(data, size=(num_samples, len(data)), replace=True).mean(axis=1)
    lower = np.quantile(samples, alpha / 2)
    upper = np.quantile(samples, 1 - alpha / 2)
    return float(lower), float(upper)


def logical_error_curve(
    df: pd.DataFrame,
    distances: Iterable[int],
    output: Path,
    title: str,
    seed: int = 0,
    x_field: str = "p",
):
    fig, ax = plt.subplots()
    for d in distances:
        subset = df[df["distance"] == d]
        subset = subset.sort_values(x_field)
        errs = subset["logical_error_rate"].to_numpy()
        probs = subset[x_field].to_numpy()
        if len(errs) == 0:
            continue
        if len(errs) > 1:
            ci = [bootstrap_ci(errs, seed=seed) for _ in errs]
            ci_low = [c[0] for c in ci]
            ci_high = [c[1] for c in ci]
        else:
            ci_low = [np.nan]
            ci_high = [np.nan]
        lower = np.maximum(np.array(errs) - np.array(ci_low), 0)
        upper = np.maximum(np.array(ci_high) - np.array(errs), 0)
        ax.errorbar(probs, errs, yerr=[lower, upper], label=f"d={d}", marker="o")
    ax.set_xlabel("Physical error p")
    ax.set_ylabel("Logical error rate")
    ax.set_yscale("log")
    ax.legend()
    ax.set_title(title)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def record_figure_command(figure_path: Path, command: str, seed: int, log_path: Path, notes: str | None = None):
    entry = {
        "figure": str(figure_path),
        "command": command,
        "seed": seed,
        "notes": notes,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
