from cProfile import label
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

import abc


class Element(metaclass=abc.ABCMeta):
    def __init__(self, _type: str, content: str) -> None:
        self.type: str = _type
        self.content: str = content
        self._label: str = "act"

    def __repr__(self) -> str:
        return f"Element(type={self.type!r}, content={self.content!r}, label={self._label!r})"

    @property
    def tag(self) -> str:
        return self._label

    def set_tag(self, tag: str):
        self.set_label(tag)

    @property
    def label(self) -> str:
        return self._label

    def set_label(self, label: str):
        self._label = label


class Text(Element):
    def __init__(self, text, label: Optional[str] = None):
        super().__init__("text", text)
        self._label = label or self._label

    def __repr__(self) -> str:
        return f"Text(type={self.type!r}, content={self.content!r}, label={self._label!r})"


class Image(Element):
    def __init__(self, url) -> None:
        super().__init__("image", url)

    def __repr__(self) -> str:
        return f"Image(type={self.type!r}, url={self.content!r}, label={self._label!r})"


class Role(Enum):
    DICER = -1
    GM = 0
    PL = 1
    OB = 2


class Message:
    def __init__(
            self,
            user_code: str,
            role: Role,
            nickname: str,
            date: str,
            elements: List[Element] = [],
    ):
        self.user_code = user_code
        self.nickname = nickname
        self.role = role
        self.date = date
        self.elements = elements

    def __repr__(self) -> str:
        return f"Message(user_code={self.user_code!r}, role={self.role}, nickname={self.nickname!r}, elements={self.elements!r}, date={self.date!r})"


class Messages(List[Message]):
    def __init__(self, messages: List[Message] = []):
        super().__init__(messages)

    def append(self, message: Message):
        return super().append(message)

    def add_message(
            self,
            user_code: str,
            role: Role,
            nickname: str,
            date: str,
            content: List[Dict[str, Any]],
    ):
        elements = []
        try:
            for ele in content:
                _type = ele["type"]
                data = ele["data"]
                if _type == "text":
                    text = data["text"]
                    elements.append(Text(text))
                elif _type == "image":
                    url = data["url"]
                    elements.append(Image(url))
        except KeyError as e:
            raise KeyError(f"Message format error. Missing key field: {e}")
        message = Message(user_code, role, nickname, date, elements)
        self.append(message)


class ExportConfig:
    def __init__(self):
        self.first_line_indent = True  # 首行缩进
        self.display_dice_command = True  # 指令显示
        self.display_external_comment = True  # 场外发言显示
        self.display_image = True  # 图片显示
        self.display_datetime = True  # 时间显示
        self.display_account = True  # 帐号显示
        self.display_year_month_day = False  # 年月日显示


class Renderer(metaclass=abc.ABCMeta):
    _PLAYER_ACTION_LABEL = "act"  # 玩家行动
    _PLAYER_SPEECH_LABEL = "speak"  # 玩家发言
    _DICE_COMMAND_LABEL = "command"  # 骰娘指令
    _EXTERNAL_COMMENT_LABEL = "outside"  # 场外发言
    _INVALID_OPERATION_LABEL = "invalid"  # 非法操作或无效操作产生的数据

    @staticmethod
    def split_and_label(text: str) -> Dict[str, str]:
        ACTION_LABEL = Renderer._PLAYER_ACTION_LABEL
        SPEECH_LABEL = Renderer._PLAYER_SPEECH_LABEL

        result_dict = {}
        inside_quote = False
        current_text = ""
        current_label = ACTION_LABEL

        for c in text:
            if c in "“”\"":
                if inside_quote:
                    result_dict[current_text] = current_label
                    current_text = ""
                    current_label = ACTION_LABEL
                    inside_quote = False
                else:
                    if current_text:
                        result_dict[current_text] = current_label
                        current_text = ""
                    current_label = SPEECH_LABEL
                    inside_quote = True
            else:
                current_text += c

        if current_text:
            final_label = SPEECH_LABEL if inside_quote else ACTION_LABEL
            result_dict[current_text] = final_label

        return result_dict

    @staticmethod
    def parse_message(message: Message, config: ExportConfig) -> Optional[Message]:

        def set_labels(elements: List[Element], new_elements: List[Element], first_label: str, other_label: str):
            if (elements_len := len(elements)) == 0:
                assert False, "Empty element list"

            first_elements = elements[0]

            first_elements.set_label(first_label)
            new_elements.append(first_elements)

            if elements_len != 1:
                for element in elements[1:]:
                    element.set_label(other_label)
                    new_elements.append(element)

        elements = message.elements

        element_len = len(elements)

        if element_len == 0:
            return None

        sender_role = message.role

        first_ele = elements[0]
        first_ele_content = first_ele.content.strip()

        is_command = first_ele_content.startswith(('.', '。', '/'))

        is_first_ele_img = isinstance(first_ele, Image)
        is_first_ele_text = isinstance(first_ele, Text)

        is_external_comment = is_first_ele_text and first_ele_content.startswith(('(', '（'))

        if sender_role == Role.DICER and not config.display_dice_command:
            return None

        if is_external_comment and not config.display_external_comment:
            return None

        if is_command and not config.display_dice_command:
            return None

        if element_len == 1 and is_first_ele_img:
            return message if config.display_image else None

        new_elements = []
        if is_first_ele_text:
            if is_command:
                set_labels(
                    elements=elements,
                    new_elements=new_elements,
                    first_label=Renderer._DICE_COMMAND_LABEL,
                    other_label=Renderer._INVALID_OPERATION_LABEL
                )
            elif is_external_comment:
                set_labels(
                    elements=elements,
                    new_elements=new_elements,
                    first_label=Renderer._EXTERNAL_COMMENT_LABEL,
                    other_label=Renderer._EXTERNAL_COMMENT_LABEL
                )
        elif is_first_ele_img:
            if config.display_image:
                new_elements.append(first_ele)
        else:
            assert False, "Encountered an unsupported element type"

        if not (is_external_comment or is_command):
            for element in elements:
                if isinstance(element, Text):
                    labeled_text = Renderer.split_and_label(element.content)
                    for text, label in labeled_text.items():
                        element_obj = Text(text, label)
                        new_elements.append(element_obj)
                elif isinstance(element, Image):
                    new_elements.append(element)
                else:
                    assert False, "Encountered an unsupported element type."

        message.elements = new_elements
        return message

    @abc.abstractmethod
    def render_message(self, message: Message) -> None:
        raise NotImplementedError

    @staticmethod
    def render(
            messages: Messages,
            renderer: "Renderer",
            config: Optional[ExportConfig] = None,
    ) -> "Renderer":
        for message in messages:
            if message := renderer.parse_message(message, config or ExportConfig()):
                renderer.render_message(message)
        return renderer

    @abc.abstractmethod
    def export(self, filename: str) -> Path:
        raise NotImplementedError
