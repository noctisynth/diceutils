from diceutils.cards import Cards, CardsManager

cards = Cards()
cards.cards_manager = CardsManager("coc.db")
cards.data = {"user1": [{}]}
cards.update("user1", 1, {"name": "New Card"})
# cards.save()
print(cards.data)
