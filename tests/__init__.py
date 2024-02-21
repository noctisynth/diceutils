from diceutils.cards import Cards, CardsManager

cards = Cards()
cards.cards_manager = CardsManager("coc.db")
cards.data = {"user1": [{}]}
cards.update("user2", 0, None)
# cards.save()
print(cards.data)
