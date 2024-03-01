class DiceutilsException(Exception):
    """Base Exception for Diceutils."""


class NoneCommandError(DiceutilsException):
    """Provided a `None` for command key."""


class TooManyAliasCommandError(DiceutilsException):
    """Too many alias command provided."""


class CommandRequired(DiceutilsException):
    """Raises when required command not provided."""


class TooManyCardsError(Exception):
    """Raises when provided number bigger than expected."""


class UnkownMode(DiceutilsException):
    """Raises when provided mode name is unkown."""
