"""
@author         :     苏向夜 <fu050409@163.com>
@date           :     March. 1st, 2024.
@description    :     This Module Provides Parser Methods or Commands on Messaging Platforms.
"""

from typing import Dict, List, Any, Sequence, Union
from diceutils.exceptions import (
    NoneCommandError,
    CommandRequired,
    TooManyAliasCommandError,
)

CommandType = Union["Optional", "Required", "Bool"]


class Optional:
    """OptionalCommand"""

    def __init__(self, key: Union[Sequence[str], str], cls: type, default: Any = None):
        if not key:
            raise NoneCommandError("Optional parameter must not be `None`.")

        if isinstance(key, str):
            key = [
                key,
            ]

        self.key = key
        self.cls = cls
        self.default = default

    def __str__(self):
        return self.key[0]


class Required:
    """Required Command."""

    def __init__(self, key, cls: type, default: Any = None):
        if not key:
            raise NoneCommandError("Required parameter must not be `None`.")

        if isinstance(key, str):
            key = [
                key,
            ]

        self.key = key
        self.cls = cls
        self.default = default

    def __str__(self):
        return self.key[0]


class Bool:
    """Bool Command."""

    def __init__(self, key, default: Union[bool, None] = None):
        if not key:
            raise NoneCommandError("Bool parameter must not be `None`.")

        if isinstance(key, str):
            key = [key]

        self.key = key
        self.default = default

    def __str__(self):
        return self.key[0]


class Positional:
    """Positional Command"""

    def __init__(self, key, cls: type, default: Any = None):
        if not key:
            raise NoneCommandError("Postional parameter must not be `None`.")

        if isinstance(key, str):
            key = [
                key,
            ]

        self.key = key
        self.cls = cls
        self.default = default

    def __str__(self):
        return self.key[0]


class Commands(List[CommandType]):
    """Command List."""

    def __init__(self, *args, **kwargs):
        super(Commands, self).__init__(*args, **kwargs)

    def __required__(self) -> List[Required]:
        return [required for required in self if isinstance(required, Required)]

    def __optional__(self) -> List[Optional]:
        return [optional for optional in self if isinstance(optional, Optional)]

    def __positional__(self) -> List[Positional]:
        return [positional for positional in self if isinstance(positional, Positional)]

    def get_plain_required(self) -> List[str]:
        return [str(required) for required in self if isinstance(required, Required)]

    def get_plain_optional(self) -> List[str]:
        return [str(optional) for optional in self if isinstance(optional, Optional)]

    def get_plain_positional(self) -> List[str]:
        return [
            str(positional) for positional in self if isinstance(positional, Positional)
        ]

    def get_plain_commands(self) -> List[str]:
        return [str(command) for command in self]


def required(commands: Commands):
    """Expand required commands from `Commands` instance."""
    return commands.__required__()


def optional(commands: Commands):
    """Expand optional commands from `Commands` instance."""
    return commands.__optional__()


def positional(commands: Commands):
    """Expand positional commands from `Commands` instance."""
    return commands.__positional__()


class CommandParser:
    """Command Parser
    示例:
        ```python
        cp = CommandParser(
            Commands([Optional("optional"), Required("required"), Only("bool"), ...]),
            args = ["required", "valueofrequired", "bool"],
            auto = True # 自动解析指令, `auto=True`时, `args`不得为空
            ).results
        print(cp["optional"]) # 输出为`None`
        print(cp["required"]) # 输出为`valueofrequired`
        print(cp["bool"]) # 输出为`True`
        ```
    """

    def __init__(
        self,
        commands: Union[Commands, None] = None,
        args: Union[List[str], None] = None,
        auto: bool = False,
    ):
        self.results: Dict[str, bool] = {}

        if not isinstance(commands, Commands):
            raise TypeError("指令槽必须为类`Commands`.")
        if args and not isinstance(args, (list, tuple)):
            raise TypeError("参数槽必须为列或数组.")

        self.commands: Commands = commands
        self.args = list(args or [])
        self.nothing = False

        if auto:
            self.shlex()

    def shlex(self, args: Union[Sequence[str], None] = None):
        """Start to parser a splited command."""
        if not args:
            args = self.args
        iter_args = [arg for arg in args]

        if not isinstance(args, (list, tuple)):
            raise TypeError("指令切片必须传入列或数组.")

        results: Dict[str, bool] = {}
        nothing: bool = True

        for command in self.commands:
            key = list(set(command.key) & set(args))
            if len(key) > 1:
                raise TooManyAliasCommandError("Too many alias parameters.")

            if isinstance(command, Bool):
                if key:
                    results[command.key[0]] = True
                    iter_args.remove(key[0])
                    nothing = False
                else:
                    results[command.key[0]] = False
                continue

            if key:
                index = args.index(key[0])
                iter_index = iter_args.index(key[0])
                if len(args) > index + 1:
                    try:
                        value = command.cls(args[index + 1])
                    except ValueError:
                        raise TypeError(
                            f"Value type of {command.key} is mismatch, {command.key} required but {type(args[index+1])} was given."
                        )
                    results[command.key[0]] = value
                    iter_args.pop(iter_index)
                    iter_args.pop(iter_index)
                    nothing = False
                else:
                    results[command.key[0]] = command.default
            else:
                if isinstance(command, Required):
                    raise CommandRequired(
                        f"Required parameter `{command.key[0]}` not found."
                    )

                results[command.key[0]] = command.default

        positional_commands = positional(self.commands)
        str_positionals = self.commands.get_plain_positional()
        for positional_command in positional_commands:
            if len(iter_args) == 0:
                break

            index = str_positionals.index(str(positional_command))
            if len(iter_args) >= index + 1:
                try:
                    value = positional_command.cls(iter_args[index])
                except ValueError:
                    raise TypeError(
                        f"Value type of {positional_command.key} is mismatch, {positional_command.key} required but {type(iter_args[index])} was given."
                    )
                results[str(positional_command)] = value
                nothing = False

        self.results = results
        self.nothing = nothing

    def __iter__(self):
        return iter(self.results.items())
