import time
import pytest
from diceutils.cards import CachedProperty


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @CachedProperty
    def area(self):
        print("Calculating area...")
        time.sleep(1)
        return 3.14 * self.radius**2

    @property
    def area_no_cached(self):
        print("Calculating area...")
        time.sleep(1)
        return 3.14 * self.radius**2


@pytest.fixture
def circle_instance():
    return Circle(5)


def test_cached_property(circle_instance):
    start_time = time.time()
    area1 = circle_instance.area
    first_access_time = time.time() - start_time

    start_time = time.time()
    area2 = circle_instance.area
    second_access_time = time.time() - start_time

    assert (
        area1 == area2
    ), "CachedProperty should return the same value on subsequent accesses"
    assert (
        first_access_time > second_access_time
    ), "CachedProperty should return the value faster on subsequent accesses"


def test_uncached_property(circle_instance):
    start_time = time.time()
    area1 = circle_instance.area_no_cached
    third_access_time = time.time() - start_time

    assert (
        third_access_time > 1
    ), "Uncached property should take at least 1 second to calculate"


if __name__ == "__main__":
    pytest.main()
