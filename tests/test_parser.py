from diceutils.parser import Bool, CommandParser, Commands, Optional, Positional


def test_parset():
    cp = CommandParser(
        Commands(
            [
                Positional("roll", int),
                Bool("cache"),
                Positional("test", int),
                Optional("age", int),
                Optional(("name", "n"), str, "欧若可"),
                Optional("sex", str),
            ]
        ),
    )
    cp.args = ["cache", "age", "20", "7", "10"]
    cp.shlex()
    assert isinstance(cp.results["roll"], int)
    assert cp.results["name"] == "欧若可"
    assert cp.results == {'roll': 7, 'cache': True, 'test': 10, 'age': 20, 'name': '欧若可', 'sex': None}
