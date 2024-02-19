import pytest
from infini.input import Input
from diceutils.cards import Cards, CardsManager, MAX_CARDS_PER_USER


# Another Mock Input Class.
class MockInput:
    def __init__(self, user_id):
        self.user_id = user_id


input_obj = Input("test_user_id")


class TestCards:
    # Test for initialization.
    def test_init(self):
        cards = Cards("Test Mode")
        assert cards.mode == "Test Mode"
        assert cards.data == {}

    # Test for save and load.
    def test_save_load(self):
        cards = Cards("Test Mode")
        cards.data = {
            "card1": {"name": "Alice", "age": 25},
            "card2": {"name": "Bob", "age": 30},
        }
        cards.save()
        assert cards.data == {}
        cards.load()
        assert cards.data == {
            "card1": {"name": "Alice", "age": 25},
            "card2": {"name": "Bob", "age": 30},
        }

    # Test for update method.
    def test_update(self):
        cards = Cards("Test Mode")
        cards.update(input_obj, {"name": "Charlie", "age": 35}, "card3")
        assert cards.data == {"card3": {"name": "Charlie", "age": 35}}

    # Test for get method.
    @pytest.mark.parametrize(
        "input_data, qid, expected_output",
        [
            (input_obj, "card1", {"name": "Alice", "age": 25}),
            (input_obj, "card2", {"name": "Bob", "age": 30}),
            (input_obj, "card3", {}),
        ],
    )
    def test_get(self, input_data, qid, expected_output):
        cards = Cards("Test Mode")
        cards.data = {
            "card1": {"name": "Alice", "age": 25},
            "card2": {"name": "Bob", "age": 30},
        }
        assert cards.get(input_data, qid) == expected_output

    # Test for delete method.
    @pytest.mark.parametrize(
        "input_data, qid, expected_output, expected_data",
        [
            (input_obj, "card1", True, {"card2": {"name": "Bob", "age": 30}}),
            (input_obj, "card2", True, {"card1": {"name": "Alice", "age": 25}}),
            (
                input_obj,
                "card3",
                False,
                {
                    "card1": {"name": "Alice", "age": 25},
                    "card2": {"name": "Bob", "age": 30},
                },
            ),
        ],
    )
    def test_delete(self, input_data, qid, expected_output, expected_data):
        cards = Cards("Test Mode")
        cards.data = {
            "card1": {"name": "Alice", "age": 25},
            "card2": {"name": "Bob", "age": 30},
        }
        assert cards.delete(input_data, qid) == expected_output
        assert cards.data == expected_data


# Test for Initialization function and save data.
def test_cards_manager():
    manager = CardsManager(":memory:")
    manager.save("test_user_id", {"card1": {"name": "Alice", "age": 25}})
    assert manager.load("test_user_id") == {"card1": {"name": "Alice", "age": 25}}


# Test for cards manager with MaxCardNumber in memory.
def test_max_cards_per_user():
    manager = CardsManager(":memory:")
    with pytest.raises(ValueError):
        manager.save(
            "test_user_id",
            {
                "card1": {"name": "Alice", "age": 25},
                "card2": {"name": "Bob", "age": 30},
                "card3": {"name": "Charlie", "age": 35},
                "card4": {"name": "David", "age": 40},
                "card5": {"name": "Eve", "age": 45},
                "card6": {"name": "Frank", "age": 50},
            },
        )


if __name__ == "__main__":
    pytest.main()
