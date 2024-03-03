# class DocxRenderer(Renderer):
#     document: DocumentType

#     def __init__(self) -> None:
#         self.document = Document()
#         self.document.styles["Normal"].font.name = "SimSun"

#     def export(self) -> None:
#         self.document.save("a.docx")

#     def render_message(self, message: Message) -> None:
#         paragraph = self.document.add_paragraph()
#         for element in message.elements:
#             if element.type == "text":
#                 if element.tag == "act":
#                     run = paragraph.add_run(element.content)
#                     run.bold = True
#                     run.font.name = "SimSun"
#                 elif element.tag == "outside":
#                     paragraph.add_run("（")
#                     content = element.content.strip("（）()")
#                     run = paragraph.add_run(content)
#                     run.font.color.rgb = (207, 210, 210)
#                     run.font.name = "SimSun"
#                 elif element.tag == "speak":
#                     content = element.content.strip('“”""')
#                     paragraph.add_run("“")
#                     run = paragraph.add_run(content)
#                     run.font.name = "Microsoft YaHei"
#                     paragraph.add_run("”")
#             else:
#                 # self.document.add_picture()
#                 ...

#         return
