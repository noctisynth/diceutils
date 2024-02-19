import time

from diceutils.cards import CachedProperty


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @CachedProperty
    def area(self):
        print("Calculating area...")
        time.sleep(1)
        return 3.14 * self.radius**2

    def area_no_cached(self):
        print("Calculating area...")
        time.sleep(1)
        return 3.14 * self.radius**2


my_circle = Circle(5)

start_time = time.time()
print(my_circle.area)
print("First access time:", time.time() - start_time)

start_time = time.time()
print(my_circle.area)
print("Second access time:", time.time() - start_time)

start_time = time.time()
print(my_circle.area_no_cached())
print("Third access time:", time.time() - start_time)
