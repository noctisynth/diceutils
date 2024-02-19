import pytest
from diceutils.cards import CachedProperty

# Test class to apply CachedProperty decorator
class TestClass:
    def __init__(self, value):
        self._value = value

    @CachedProperty
    def value(self):
        return self._value

# Happy path tests with various realistic test values
@pytest.mark.parametrize("test_id, initial_value, expected_value", [
    ("HP_01", 10, 10),
    ("HP_02", "test", "test"),
    ("HP_03", [1, 2, 3], [1, 2, 3]),
    ("HP_04", {"key": "value"}, {"key": "value"}),
])
def test_cached_property_happy_path(test_id, initial_value, expected_value):
    # Arrange
    test_obj = TestClass(initial_value)

    # Act
    result = test_obj.value

    # Assert
    assert result == expected_value, f"Test ID {test_id}: CachedProperty did not return the expected value."

# Edge case tests
@pytest.mark.parametrize("test_id, initial_value, modify_value, expected_value", [
    ("EC_01", 10, 20, 10),  # Changing the underlying value doesn't affect the cached value
])
def test_cached_property_edge_cases(test_id, initial_value, modify_value, expected_value):
    # Arrange
    test_obj = TestClass(initial_value)

    # Act
    _ = test_obj.value  # Access the property to cache the value
    test_obj._value = modify_value  # Attempt to change the underlying value
    result = test_obj.value  # Access the property again

    # Assert
    assert result == expected_value, f"Test ID {test_id}: CachedProperty did not maintain the initial cached value."

# Error case tests
@pytest.mark.parametrize("test_id, initial_value, expected_exception", [
    ("ER_01", None, AttributeError),  # Accessing the property on None should raise an AttributeError
])
def test_cached_property_error_cases(test_id, initial_value, expected_exception):
    # Arrange
    test_obj = TestClass(initial_value)

    # Act / Assert
    with pytest.raises(expected_exception):
        _ = test_obj.value
        pytest.fail(f"Test ID {test_id}: CachedProperty should have raised an exception.")

# Test to ensure cache is instance-specific and not shared between instances
def test_cached_property_instance_specific():
    # Arrange
    test_obj1 = TestClass(10)
    test_obj2 = TestClass(20)

    # Act
    result1 = test_obj1.value
    result2 = test_obj2.value

    # Assert
    assert result1 != result2, "CachedProperty cache should be instance-specific and not shared between instances."

# Test to ensure that accessing the property on the class returns the CachedProperty instance itself
def test_cached_property_access_on_class():
    # Act
    result = TestClass.value

    # Assert
    assert isinstance(result, CachedProperty), "Accessing the property on the class should return the CachedProperty instance itself."
