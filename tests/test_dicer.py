from diceutils.dicer import Dicer


def test_dicer_check():
    assert Dicer.check("1")
    assert Dicer.check("1d2")
