from typing import Optional
from diceutils.renderer._models import Renderer, Message

from pathlib import Path

from docx.enum.style import WD_STYLE_TYPE
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn


class DocxRenderer(Renderer):

    def __init__(self) -> None:
        self.document = Document()
        self._add_chinese_font_style("微软雅黑")
        self._add_chinese_font_style("SimSun", "SimSun-ExtB")

    def _add_chinese_font_style(self, style_name: str, font_name: Optional[str] = None, font_size: float = 11.0):
        font_name = font_name or style_name
        style_song = self.document.styles.add_style(style_name, WD_STYLE_TYPE.CHARACTER)
        style_song.font.name = font_name
        style_song.font.size = Pt(font_size)
        style_song.element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

    def export(self, filename: str) -> Path:
        filepath = Path("./exports/" + filename + ".docx").resolve()

        filepath.parent.mkdir(parents=True, exist_ok=True)
        self.document.save(str(filepath))

        return filepath

    def render_message(self, message: Message) -> None:
        paragraph = self.document.add_paragraph()
        for element in message.elements:
            if element.type == "text":
                if element.tag == "act":
                    run = paragraph.add_run(element.content, style="SimSun")

                elif element.tag == "outside":
                    content = element.content.strip("（）()")
                    run = paragraph.add_run(content, style="SimSun")

                elif element.tag == "speak":
                    run = paragraph.add_run(f"“{element.content}”", style="微软雅黑")

            else:
                # self.document.add_picture()
                ...

        return
