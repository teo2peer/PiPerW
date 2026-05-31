from PiPerW.utils.memory import available_mb, under_pressure


def test_available_mb_returns_int():
    mb = available_mb()
    assert isinstance(mb, int)


def test_under_pressure_bool():
    assert under_pressure(0) is False
