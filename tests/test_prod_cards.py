from diceutils.cards import Cards, MAX_CARDS_PER_USER
from diceutils.exceptions import TooManyCardsError


def test_card():
    cards = Cards("coc")
    cards.clear("0")

    cards.update("0", attributes={"name": "简律纯"})
    cards.update("0", 1, attributes={"name": "雪花"})
    assert cards.get("0") == {"name": "简律纯"}
    cards.select("0", 1)
    assert cards.get("0") == {"name": "雪花"}

    for _ in range(MAX_CARDS_PER_USER - 2):
        cards.new("0")

    try:
        cards.new("0")
        exception = None
    except Exception as err:
        exception = err
    finally:
        assert isinstance(exception, TooManyCardsError)
