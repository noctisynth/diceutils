class DiceutilsException(Exception): ...


class NoneTypeCommandError(DiceutilsException): ...


class TooManyAliasCommandError(DiceutilsException): ...


class CommandRequired(DiceutilsException): ...


class TooManyCardsError(Exception):
    """单个用户缓存中存储的卡数量过多"""


class UnkownMode(DiceutilsException): ...
