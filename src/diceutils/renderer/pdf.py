# class PDFRenderer(Renderer):
#     _canvas: canvas.Canvas

#     def __init__(self) -> None:
#         self._canvas = canvas.Canvas(str(random.randbytes(5)) + ".pdf")

#     def export(self, filename: str) -> None:
#         return self._canvas._doc.SaveToFile(filename=filename, canvas=self._canvas)

#     def render_message(self, message: Message):
#         self._canvas.drawText(Paragraph("dde"))
#         for element in message.elements:
#             if element.type == "text":
#                 if element.tag == "act":
#                     ...
#                 elif element.tag == "outside":
#                     ...
#                 elif element.tag == "speak":
#                     ...
