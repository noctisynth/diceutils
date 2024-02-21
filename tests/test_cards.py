from diceutils.cards import Cards, cached_method, CardsManager

coc_card = Cards("coc")
coc_card.cards_manager = CardsManager("coc.db")
coc_card.data = {"pl1": [{}], "pl2": [{}]}
coc_card.save()

coc_card.load({"pl1", "pl2"})
print(coc_card.data)

# coc_card.update()

coc_card.data["pl1"].update({"hp": 12})
print(coc_card.data)

coc_card.update({"pl9": {"hp": 10}})
print(coc_card.data)
coc_card.save()
