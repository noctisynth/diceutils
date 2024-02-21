class NoneTypeCommandError(Exception): ...


class TooManyAliasCommandError(Exception): ...


class CommandRequired(Exception): ...


class TooManyCardsError(Exception):
    """单个用户缓存中存储的卡数量过多"""
