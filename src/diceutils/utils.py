from infini.input import Input
from infini.typing import List

import re


def get_user_id(input: Input) -> str:
    return input.variables.get("user_id", "0")


def get_group_id(input: Input):
    return (
        input.variables.get("group_id")
        or input.variables.get("session_id")
        or input.variables.get("user_id")
        or "0"
    )


def translate_punctuation(string: str) -> str:
    """中文字符转换为英文字符"""
    punctuation_mapping = {
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "；": ";",
        "：": ":",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "《": "<",
        "》": ">",
    }
    for ch_punct, en_punct in punctuation_mapping.items():
        string = string.replace(ch_punct, en_punct)
    return string


def format_str(message: str, begin=None, lower=True) -> str:
    regex = r"[<\[](.*?)[\]>]"
    message = str(message).lower() if lower else str(message)
    msg = translate_punctuation(
        re.sub(r"\s+", " ", re.sub(regex, "", message)).strip(" ")
    )
    if msg.startswith("/"):
        msg = "." + msg[1:]

    if begin:
        if isinstance(begin, str):
            begin = [
                begin,
            ]
        elif isinstance(begin, tuple):
            begin = list(begin)

        begin.sort(reverse=True)
        for b in begin:
            msg = msg.replace(b, "").lstrip(" ")

    return msg


def format_msg(message, begin=None, zh_en=True) -> List[str]:
    msgs = format_str(message, begin=begin)
    outer = []
    regex = (
        r'([+-]?\d+(?:d\d+)?)|("[^"]+")|([a-zA-Z\u4e00-\u9fa5]+)'
        if not zh_en
        else r'([+-]?\d+)|([a-zA-Z]+)|("[^"]+")|([\u4e00-\u9fa5]+)'
    )
    msgs = list(filter(None, re.split(regex, msgs)))

    for msg in msgs:
        splited_msg = list(filter(None, re.split(regex, msg.strip(" "))))

        for i, msg in enumerate(splited_msg):
            splited_msg[i] = msg.strip('"')

        outer += splited_msg

    msgs = list(filter(None, outer))
    return msgs
