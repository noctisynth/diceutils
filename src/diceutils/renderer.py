from enum import Enum
from typing import Dict, List, Any, Self, Type, Optional
import abc, re, datetime


class Element(abc.ABC):
    def __init__(self, _type: str, content: str) -> None:
        self.type: str = _type
        self.content: str = content

    def __repr__(self) -> str:
        return f"Element(type={self.type}, content={self.content})"


class Text(Element):
    def __init__(self, text, tags: List = []):
        super().__init__("text", text)
        self.tags = tags

    def __repr__(self) -> str:
        if len(self.tags) == 0:
            return f"Text({self.content!r})"
        else:
            return f"Text(content={self.content!r}, tags={self.tags})"

    def add_tag(self, tag: str):
        self.tags.append(tag)

    def add_tags(self, tags: List[str] = []):
        for tag in tags:
            self.tags.append(tag)


class Image(Element):
    def __init__(self, url) -> None:
        super().__init__("image", url)

    def __repr__(self) -> str:
        return f"Image({self.content!r})"


class Role(Enum):
    DICER = -1,
    GM = 0,
    PL = 1,
    OB = 2,


class Message:
    def __init__(self, user_code: str, role: Role, nickname: str, date: datetime.datetime,
                 elements: List[Element] = []):
        self.user_code = user_code
        self.nickname = nickname
        self.role = role
        self.date = date
        self.elements = elements

    def __repr__(self) -> str:
        return f"Message(user_code={self.user_code}, role={self.role}, nickname={self.nickname}, elements={self.elements}, date={self.date})"


class Messages(list):

    def __init__(self, messages: List[Message] = []):
        super().__init__(messages)

    def append(self, message: Message):
        return super().append(message)

    def add_message(self, user_code: str, role: Role, nickname: str, date, content: List[Dict[str, Any]]):
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
        self.dice_command_filter = False  # 骰子指令过滤
        self.external_comment_filter = False  # 场外发言过滤
        self.display_image = True  # 图片显示
        self.display_datetime = True  # 时间显示
        self.display_account = True  # 帐号显示
        self.display_year_month_day = False  # 年月日显示


class IRenderer(abc.ABC):
    name: str

    def __init__(self, msgs: Messages, config: ExportConfig, path: str):
        self.raw_messages: Messages = msgs
        self.parsed_messages: Messages = Messages()
        self.config: ExportConfig = config
        self.path: str = path

    @staticmethod
    def split_and_label(text: str) -> Dict[str, str]:
        pattern = r'“[^”]*”|[^“”]+'
        parts = re.findall(pattern, text)

        result_dict = {}

        for part in parts:
            if part.startswith('“') and part.endswith('”'):
                result_dict[part] = 'speak'
            else:
                result_dict[part] = 'act'

        return result_dict

    def render_message(self, message: Message) -> Optional[Message]:
        config = self.config
        elements = message.elements

        if config.dice_command_filter and message.role == -1:
            return None

        if len(elements) == 1 and isinstance(elements[0], Image):
            return message if config.display_image else None

        ele_iter = iter(elements)
        first_ele = next(ele_iter)
        is_external_comment = first_ele.content.startswith(("(", "（"))
        is_text = isinstance(first_ele, Text)
        if config.external_comment_filter and is_text and is_external_comment:
            return None

        if is_text and is_external_comment:
            first_ele.add_tag("outside")
            for ele in ele_iter:
                if isinstance(ele, Text):
                    ele.add_tag("outside")
            return message

        new_elements = []
        if is_text:
            for text, tag in self.split_and_label(first_ele.content).items():
                new_elements.append(Text(text, [tag]))

        for ele in ele_iter:
            if isinstance(ele, Text):
                for text, tag in self.split_and_label(ele.content).items():
                    new_elements.append(Text(text, [tag]))

        message.elements = new_elements
        return message

    def render(self) -> Self:
        for msg in self.raw_messages:
            message = self.render_message(msg)
            if message:
                self.parsed_messages.append(message)
        return self

    @abc.abstractmethod
    def export(self) -> None:
        pass


class DocxRenderer(IRenderer):
    name: str = "docx"

    def export(self) -> None:
        pass


def generate(path: str, msgs: Messages, renderer: Type[IRenderer], config: Optional[ExportConfig] = None) -> IRenderer:
    if not config:
        config = ExportConfig()
    return renderer(msgs, config, path).render()
