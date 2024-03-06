from diceutils.renderer._models import Renderer, Message, Role, Element
from pathlib import Path

import html

_style_sheet = """
<style>
*, :before, :after {
    box-sizing: border-box;
}

body {
    margin: 0;
    width: 100%;
    font-family: "Chinese Quotes", "Inter var", "Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Helvetica, Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";;
    font-weight: 400;
    color: #3c3c43;
    background-color: #f6f6f7;
    font-synthesis: style;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img {
    max-width: 100%;
    height: auto;
}

hr {
    width: 100%;
}

h1 {
    margin-bottom: 2px;
}

p {
    white-space: pre-wrap;
}

.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: auto;
    background-color: #555;
    color: #fff;
    text-align: center;
    padding: 5px;
    border-radius: 6px;

    /* Position the tooltip text */
    position: absolute;
    z-index: 1;
    bottom: calc(100% + 5px);
    left: calc(50% + 50px);
    margin-left: -60px;

    /* Fade in tooltip */
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip .tooltiptext::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #555 transparent transparent transparent;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

.flex {
    display: flex;
}

.flex-col {
    flex-direction: column;
}

.flex-row {
    flex-direction: row;
}

.items-center {
    align-items: center;
}

.items-start {
    align-items: start;
}

.justify-center {
    justify-content: center;
}

.justify-start {
    justify-content: start;
}

.text-coolGray {
    color: rgb(207, 210, 210);
}

.text-kai {
    font-family: 楷体, Microsoft Yahei, Arial;
    font-size: 1.1rem;
}

.text-italic {
    font-style: italic;
}

.text-simsun {
    font-family: Cascadia Mono, SimSun, Microsoft Yahei, Arial;
}

.text-cascadia {
    font-family: Cascadia Mono, Arial;
}

.text-2 {
    font-size: 0.6rem;
}

.w-full {
    width: 100%;
}

.pr-1 {
    padding-right: 0.6rem;
}

.w-4 {
    width: 5rem;
}

.m-2 {
    margin: 2rem;
}

.flex-wrap {
    flex-wrap: wrap;
}
</style>
"""


class HTMLRenderer(Renderer):
    plain_text: str

    def __init__(self) -> None:
        self.plain_text = ""

    def _render_user(self, message: Message):
        return (
            f'<div class="flex items-start justify-center flex-col w-4">'
            f'<span class="text-2">{message.role.name}</span>'
            f"<span>{message.nickname}</span>"
            "</div>"
        )

    def _render_keeper(self, element: Element):
        return f'<span class="text-kai">{html.escape(element.content)}</span>'

    def _render_act(self, element: Element, is_first: bool = False):
        content = "#" + element.content.strip("#＃") if is_first else element.content
        return f'<span class="text-simsun text-italic">{html.escape(content)}</span>'

    def _render_dicer(self, element: Element) -> str:
        return f"<span>{html.escape(element.content)}</span>"

    def _render_command(self, element: Element) -> str:
        return f'<span class="text-cascadia">{html.escape(element.content)}</span>'

    def _render_speak(self, element: Element) -> str:
        content = "“" + element.content.strip('"“”') + "”"
        return f'<span class="text-simsun">{html.escape(content)}</span>'

    def _render_outside(self, element: Element) -> str:
        content = "（" + element.content.strip("()（）") + "）"
        return f'<span class="flex items-center justify-center text-coolGray">{html.escape(content)}</span>'

    def _render_image(self, image: Element) -> str:
        return f'<span><img src="{image.content}"></img></span>'

    def render_message(self, message: Message) -> None:
        text = " " * 6
        text += (
            '<div class="flex items-center justify-start flex-row w-full flex-wrap">'
        )
        text += self._render_user(message)
        text += '<div><p class="tooltip">'
        for index, element in enumerate(message.elements):
            is_first = index == 0
            if element.type == "text":
                if message.role == Role.DICER:
                    text += self._render_dicer(element)
                    continue
                elif message.role == Role.OB:
                    text += self._render_outside(element)
                    continue

                if element.tag == "act":
                    if message.role == Role.GM:
                        text += self._render_keeper(element)
                    else:
                        text += self._render_act(element, is_first=is_first)
                elif element.tag == "outside":
                    text += self._render_outside(element)
                elif element.tag == "speak":
                    text += self._render_speak(element)
                elif element.tag == "command":
                    text += self._render_command(element)
            elif element.type == "image":
                text += self._render_image(element)
        text += f'<span class="tooltiptext">{message.date}</span></p></div>'
        text += "</div>\n"
        self.plain_text += text

    def _generate(self, filename: str) -> str:
        text = "<!DOCTYPE html>\n"
        text += '<html lang="zh-CN">\n'
        text += "  <head>\n"
        text += '    <meta charset="utf-8">\n'
        text += (
            '    <meta name="viewport" content="width=device-width,initial-scale=1">\n'
        )
        text += "    <title>" + filename + "</title>\n"
        text += '    <meta name="description" content="DicerGirl 4 导出日志">\n'
        text += "  </head>\n\n"
        text += "  <body>\n"
        text += '    <div class="m-2 flex items-start justify-center flex-col">\n'
        text += f"      <h1>{filename}</h1><hr />\n"
        text += self.plain_text
        text += "    </div>\n"
        text += "  </body>\n"
        text += _style_sheet
        text += "</html>"
        return text

    def export(self, filename: str) -> Path:
        text = self._generate(filename)
        filepath = Path("./exports/" + filename + ".html").resolve()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(text, encoding="utf-8")
        return filepath
