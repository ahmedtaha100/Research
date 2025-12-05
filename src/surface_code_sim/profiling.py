import time
from dataclasses import dataclass
from typing import Callable, Dict, List

from surface_code_sim.cli import _run_once, _sweep_configs


@dataclass
class ProfileResult:
    label: str
    duration_seconds: float


def profile_run(fn: Callable[[], None], label: str) -> ProfileResult:
    start = time.time()
    fn()
    return ProfileResult(label=label, duration_seconds=time.time() - start)


def profile_samplers() -> Dict[str, float]:
    configs = _sweep_configs(
        distances=[3, 5],
        p_values=[0.001],
        backends=["aer", "stim"],
        decoders=["local"],
        rounds=2,
        shots=100,
        px=None,
        py=None,
        pz=None,
        readout_error=0.0,
        readout_error_0to1=None,
        readout_error_1to0=None,
        base_seed=0,
    )
    results: List[ProfileResult] = []
    for cfg in configs:
        run_id = f"profile-{cfg.backend}-{cfg.distance}"
        results.append(profile_run(lambda cfg=cfg: _run_once(cfg, git_sha="unknown", run_id=run_id), label=run_id))
    return {r.label: r.duration_seconds for r in results}


if __name__ == "__main__":
    times = profile_samplers()
    for label, duration in times.items():
        print(f"{label}: {duration:.3f}s")
