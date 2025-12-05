from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal

ALLOWED_DISTANCES = (3, 5, 7, 9)
ALLOWED_DECODERS = ("local", "mwpm")
ALLOWED_BACKENDS = ("aer", "stim")

CSV_FIELDS = [
    "run_id",
    "git_sha",
    "seed",
    "distance",
    "rounds",
    "shots",
    "decoder",
    "backend",
    "p",
    "px",
    "py",
    "pz",
    "readout_error",
    "readout_error_0to1",
    "readout_error_1to0",
    "logical_error_rate",
    "ci_low",
    "ci_high",
    "wall_time_seconds",
    "timestamp_utc",
]


@dataclass
class NoiseParams:
    model: Literal["depolarizing", "biased_pauli"] = "depolarizing"
    p: float = 0.0
    readout_error: float = 0.0
    readout_error_0to1: float | None = None
    readout_error_1to0: float | None = None
    px: float | None = None
    py: float | None = None
    pz: float | None = None

    def validate(self) -> None:
        if self.model not in ("depolarizing", "biased_pauli"):
            raise ValueError(f"Unsupported noise model: {self.model}")
        if not 0 <= self.readout_error <= 1:
            raise ValueError("readout_error must be in [0,1]")
        if (self.readout_error_0to1 is None) != (self.readout_error_1to0 is None):
            raise ValueError("readout_error_0to1 and readout_error_1to0 must both be set or both None")
        if self.readout_error_0to1 is not None:
            if not 0 <= self.readout_error_0to1 <= 1 or not 0 <= self.readout_error_1to0 <= 1:
                raise ValueError("readout_error_0to1 and readout_error_1to0 must be in [0,1]")
        if self.model == "depolarizing":
            if not 0 <= self.p <= 1:
                raise ValueError("p must be in [0,1] for depolarizing noise")
            self.px = self.py = self.pz = None
        else:
            for name, val in ("px", self.px), ("py", self.py), ("pz", self.pz):
                if val is None or not 0 <= val <= 1:
                    raise ValueError(f"{name} must be set in [0,1] for biased Pauli noise")
            total = float(self.px) + float(self.py) + float(self.pz)
            if total > 1:
                raise ValueError("px+py+pz must be <= 1")
            self.p = 0.0


@dataclass
class ExperimentConfig:
    distance: int
    rounds: int
    shots: int
    noise: NoiseParams
    decoder: str = "mwpm"
    backend: str = "aer"
    seed: int = 0

    def __post_init__(self) -> None:
        if self.distance not in ALLOWED_DISTANCES:
            raise ValueError(f"distance must be one of {ALLOWED_DISTANCES}")
        if self.rounds <= 0:
            raise ValueError("rounds must be positive")
        if self.shots <= 0:
            raise ValueError("shots must be positive")
        if self.decoder not in ALLOWED_DECODERS:
            raise ValueError(f"decoder must be one of {ALLOWED_DECODERS}")
        if self.backend not in ALLOWED_BACKENDS:
            raise ValueError(f"backend must be one of {ALLOWED_BACKENDS}")
        self.noise.validate()

    def to_dict(self) -> dict:
        data = asdict(self)
        data.update(
            {
                "p": self.noise.p,
                "px": self.noise.px,
                "py": self.noise.py,
                "pz": self.noise.pz,
                "readout_error": self.noise.readout_error,
                "readout_error_0to1": self.noise.readout_error_0to1,
                "readout_error_1to0": self.noise.readout_error_1to0,
            }
        )
        return data


@dataclass
class RunMetadata:
    run_id: str
    git_sha: str
    command: str
    seed: int
    started_at: datetime | None = None

    def timestamp_iso(self) -> str:
        ts = self.started_at or datetime.now(timezone.utc)
        return ts.astimezone(timezone.utc).isoformat()

    def for_csv(self) -> dict:
        return {
            "run_id": self.run_id,
            "git_sha": self.git_sha,
            "seed": self.seed,
            "timestamp_utc": self.timestamp_iso(),
            "command": self.command,
        }


def make_csv_row(
    *,
    metadata: RunMetadata,
    config: ExperimentConfig,
    logical_error_rate: float,
    ci_low: float | None,
    ci_high: float | None,
    wall_time_seconds: float,
) -> dict:
    row = {field: None for field in CSV_FIELDS}
    row.update({
        "run_id": metadata.run_id,
        "git_sha": metadata.git_sha,
        "seed": metadata.seed,
        "distance": config.distance,
        "rounds": config.rounds,
        "shots": config.shots,
        "decoder": config.decoder,
        "backend": config.backend,
        "p": config.noise.p,
        "px": config.noise.px,
        "py": config.noise.py,
        "pz": config.noise.pz,
        "readout_error": config.noise.readout_error,
        "readout_error_0to1": config.noise.readout_error_0to1,
        "readout_error_1to0": config.noise.readout_error_1to0,
        "logical_error_rate": logical_error_rate,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "wall_time_seconds": wall_time_seconds,
        "timestamp_utc": metadata.timestamp_iso(),
    })
    return row


@dataclass
class FigureCommand:
    figure_path: str
    command: str
    seed: int
    notes: str | None = None

    def serialize(self) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        parts = [f"timestamp={timestamp}", f"figure={self.figure_path}", f"seed={self.seed}", f"cmd={self.command}"]
        if self.notes:
            parts.append(f"notes={self.notes}")
        return " | ".join(parts)
