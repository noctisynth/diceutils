import pprint
from diceutils.cards import Cards, cached_method, CardsManager

pp = pprint.PrettyPrinter(depth=2)

coc_card = Cards("coc")
coc_card.cards_manager = CardsManager(":memory:", max_cards_per_user="2")
coc_card.data = {
    "阿水": [
        {"name": "Bob", "age": 20},
        {"name": "Alice", "age": 27},
        {"name": "Alice", "age": 27},
    ],
    "小苏": [{"name": "Tom", "age": 18}],
    "雪花": [
        {"name": "Jack", "age": 20},
        {"name": "Jack", "age": 20},
        {"name": "Jack", "age": 20},
        {"name": "Jack", "age": 20},
        {"name": "Jack", "age": 20},
        # {"name": "Jack", "age": 20}, # will raise TooManyCardsError
    ],
}
coc_card.save()

pp.pprint(coc_card.data)
