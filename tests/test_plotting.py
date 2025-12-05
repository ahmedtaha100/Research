import numpy as np
import pandas as pd

from surface_code_sim.plotting import bootstrap_ci, logical_error_curve


def test_bootstrap_ci_returns_bounds():
    data = np.array([0, 1, 0, 1])
    low, high = bootstrap_ci(data, num_samples=1000, alpha=0.1, seed=0)
    assert 0 <= low <= high <= 1


def test_logical_error_curve_writes_file(tmp_path):
    df = pd.DataFrame(
        {
            "distance": [3, 3, 5, 5],
            "p": [0.001, 0.005, 0.001, 0.005],
            "logical_error_rate": [0.1, 0.2, 0.05, 0.1],
        }
    )
    out = tmp_path / "fig.png"
    logical_error_curve(df, distances=[3, 5], output=out, title="demo", seed=0, x_field="p")
    assert out.exists()
