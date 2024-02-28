from diceutils.status import StatusPool, StatusManager
import pytest


@pytest.fixture
def status():
    StatusPool.register("dicergirl")
    return StatusPool.get("dicergirl")


def test_manager_init():
    manager = StatusManager()
    manager.load()


def test_init(status):
    assert isinstance(status.data, dict)


def test_set_bool(status):
    status.set("0", "command", status=False)
    assert not status.get("0", "command")
    status.set("0", "command", status=True)
    assert status.get("0", "command")


def test_set_str(status):
    status.set("0", "keeper", status="1264983312")
    assert status.get("0", "keeper") == "1264983312"
    status.set("0", "player", status=["1264983312", "3582529065"])
    assert status.get("0", "player") == ["1264983312", "3582529065"]
