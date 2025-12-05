from surface_code_sim.utils.seed import seed_everything


def test_seed_everything_is_reproducible():
    first = seed_everything(1234)
    vals1 = first["np_rng"].integers(0, 1000, size=5).tolist()

    second = seed_everything(1234)
    vals2 = second["np_rng"].integers(0, 1000, size=5).tolist()

    assert first["seed"] == 1234
    assert second["seed"] == 1234
    assert vals1 == vals2


def test_seed_everything_applies_salt_offset():
    base = seed_everything(1)["seed"]
    salted = seed_everything(1, salt=7)["seed"]

    assert base != salted
