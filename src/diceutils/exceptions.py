class DiceutilsException(Exception):
    """Base Exception for Diceutils."""


class NoneTypeCommandError(DiceutilsException): ...


class TooManyAliasCommandError(DiceutilsException): ...


class CommandRequired(DiceutilsException):
    """Raises when required command not provided."""


class TooManyCardsError(Exception):
    """Raises when provided number bigger than expected."""


class UnkownMode(DiceutilsException):
    """Raises when provided mode name is unkown."""
