import pytest
from unittest.mock import MagicMock
from diceutils.cards import Cards

# Mock CardsManager to avoid actual file I/O during tests
@pytest.fixture
def mock_cards_manager(monkeypatch):
    mock_manager = MagicMock()
    monkeypatch.setattr("diceutils.cards.CardsManager", lambda *args, **kwargs: mock_manager)
    return mock_manager

# Parametrized test for __init__ method
@pytest.mark.parametrize("mode, expected_mode", [
    ("Test Mode", "Test Mode"),  # ID: init-happy-path-1
    ("", "unknown_mode"),        # ID: init-edge-case-empty-string
    (None, "unknown_mode"),      # ID: init-edge-case-none
], ids=["init-happy-path-1", "init-edge-case-empty-string", "init-edge-case-none"])
def test_Cards_init(mock_cards_manager, mode, expected_mode):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}

    # Act
    cards = Cards(mode=mode)

    # Assert
    assert cards.mode == expected_mode
    mock_cards_manager.load.assert_called_once()

# Parametrized test for save method
@pytest.mark.parametrize("data, expected_calls", [
    ({"user1": [{"card": "Ace"}]}, 1),  # ID: save-happy-path-1
    ({}, 1),                            # ID: save-edge-case-empty-dict
], ids=["save-happy-path-1", "save-edge-case-empty-dict"])
def test_Cards_save(mock_cards_manager, data, expected_calls):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}
    cards = Cards()
    cards.data = data

    # Act
    cards.save()

    # Assert
    assert mock_cards_manager.save.call_count == expected_calls

# Parametrized test for load method
@pytest.mark.parametrize("target, expected_calls, return_value", [
    ("*", 2, (dict(), dict())),                   # ID: load-happy-path-all
    ("user1", 2, ([], 0)),                        # ID: load-happy-path-single-user
    ({"user1", "user2"}, 3, ([], 0)),             # ID: load-happy-path-multiple-users
    ("", 2, ([], 0)),                             # ID: load-edge-case-empty-string
    (set(), 1, ()),                               # ID: load-edge-case-empty-set
], ids=["load-happy-path-all", "load-happy-path-single-user", "load-happy-path-multiple-users", "load-edge-case-empty-string", "load-edge-case-empty-set"])
def test_Cards_load(mock_cards_manager, target, expected_calls, return_value):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}

    cards = Cards()

    mock_cards_manager.load.return_value = return_value
    # Act
    cards.load(target=target)

    # Assert
    assert mock_cards_manager.load.call_count == expected_calls

# Parametrized test for update method
@pytest.mark.parametrize("user_id, index, cha_dict, expected_data", [
    ("user1", 0, {"name": "New Card"}, {"user1": [{"name": "New Card"}]}),   # ID: update-happy-path-1
    ("user2", 0, None, {"user2": [{}]}),                                     # ID: update-edge-case-none-cha_dict
], ids=["update-happy-path-1", "update-edge-case-none-cha_dict"])
def test_Cards_update(mock_cards_manager, user_id, index, cha_dict, expected_data):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}
    cards = Cards()
    cards.data = {user_id: [{}]}

    # Act
    cards.update(user_id, index, cha_dict)

    # Assert
    assert cards.data == expected_data
    mock_cards_manager.save.assert_called_once_with({user_id: [expected_data[user_id][0]]}, {})

# Parametrized test for get method
@pytest.mark.parametrize("user_id, index, expected_result", [
    ("user1", None, {"card": "Ace"}),    # ID: get-happy-path-1
    ("user1", 0, {"card": "Ace"}),       # ID: get-happy-path-2
    ("user2", None, None),               # ID: get-edge-case-nonexistent-user
    ("user1", 1, None),                  # ID: get-edge-case-nonexistent-index
], ids=["get-happy-path-1", "get-happy-path-2", "get-edge-case-nonexistent-user", "get-edge-case-nonexistent-index"])
def test_Cards_get(mock_cards_manager, user_id, index, expected_result):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}
    cards = Cards()
    cards.data = {"user1": [{"card": "Ace"}]}

    # Act
    result = cards.get(user_id, index)

    # Assert
    assert result == expected_result

# Parametrized test for delete method
@pytest.mark.parametrize("user_id, index, expected_result, expected_data", [
    ("user1", None, True, {}),                             # ID: delete-happy-path-1
    ("user1", 0, True, {"user1": []}),                     # ID: delete-happy-path-2
    ("user2", None, False, {"user1": [{"card": "Ace"}]}),  # ID: delete-edge-case-nonexistent-user
    ("user1", 1, False, {"user1": [{"card": "Ace"}]}),     # ID: delete-edge-case-nonexistent-index
], ids=["delete-happy-path-1", "delete-happy-path-2", "delete-edge-case-nonexistent-user", "delete-edge-case-nonexistent-index"])
def test_Cards_delete(mock_cards_manager, user_id, index, expected_result, expected_data):
    # Arrange
    mock_cards_manager.load.return_value = {}, {}
    cards = Cards()
    cards.data = {"user1": [{"card": "Ace"}]}

    # Act
    result = cards.delete(user_id, index)

    # Assert
    assert result == expected_result
    assert cards.data == expected_data
    if expected_result:
        mock_cards_manager.save.assert_called_once()
