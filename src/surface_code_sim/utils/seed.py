from __future__ import annotations

import os
import random
from typing import Any, Dict

import numpy as np


DEFAULT_SEED_ENV = "SURFACE_CODE_SEED"


def _normalize_seed(seed: int) -> int:
    return int(seed) % (2**32)


def seed_everything(seed: int | None = None, *, salt: int = 0) -> Dict[str, Any]:
    if seed is None:
        env_seed = os.getenv(DEFAULT_SEED_ENV)
        seed = int(env_seed) if env_seed is not None else 0

    resolved_seed = _normalize_seed(seed + salt)
    random.seed(resolved_seed)
    np_rng = np.random.default_rng(resolved_seed)

    return {"seed": resolved_seed, "np_rng": np_rng}
