from diceutils.cards import Cards


def test_card():
    cards = Cards("coc")
    cards.update("0", attributes={"name": "简律纯"})
    cards.update("0", 1, attributes={"name": "雪花"})
    assert cards.get("0") == {"name": "简律纯"}
    cards.select("0", 1)
    assert cards.get("0") == {"name": "雪花"}
    assert cards.getall("0") == [{"name": "简律纯"}, {"name": "雪花"}]

