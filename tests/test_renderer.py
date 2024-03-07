from diceutils.renderer import Renderer, Messages, Role
from diceutils.renderer.docx import DocxRenderer
from diceutils.renderer.html import HTMLRenderer

import datetime


def test_render():
    messages = Messages()
    msg_content_1 = [
        {"type": "text", "data": {"text": "“你好”，PC顿了顿道，“非常好”"}},
    ]
    msg_content_2 = [
        {
            "type": "text",
            "data": {
                "text": "男人最终还是跟了上来，只是嘴里连连念叨着:“我是美国公民，我是美国公民……”"
            },
        },
    ]
    msg_content_3 = [{"type": "text", "data": {"text": ".rd10*5"}}]
    msg_content_4 = [
        {"type": "text", "data": {"text": "[苏向夜]掷骰: 1D10*5={10}*5=50"}}
    ]

    msg_content_5 = [
        {"type": "text", "data": {"text": "苏说道:”我们去毁灭人类吧。“Test，“hi"}}
    ]
    messages.add_message("230234235", Role.GM, "苏向夜", "date", msg_content_1)
    messages.add_message("130324324", Role.PL, "少年狐", "date", msg_content_1)
    messages.add_message("120232412", Role.PL, "Aruvelut", "date", msg_content_2)
    messages.add_message("230234235", Role.GM, "苏向夜", "date", msg_content_3)
    messages.add_message("3371047314", Role.DICER, "骰娘", "date", msg_content_4)
    messages.add_message("230234235", Role.GM, "苏向夜", "date", msg_content_5)
    messages.add_message(
        "130232542",
        Role.OB,
        "简律纯",
        str(datetime.datetime.now()),
        [
            {"type": "text", "data": {"text": "谴责！\n狠狠谴责！"}},
            {
                "type": "image",
                "data": {
                    "url": "https://th.bing.com/th/id/OIP.ZTTJgCn_iXE4sM52RK2x7gAAAA?rs=1&pid=ImgDetMain"
                },
            },
        ],
    )
    messages.add_message(
        "130232542",
        Role.OB,
        "简律纯",
        str(datetime.datetime.now()),
        [
            {
                "type": "image",
                "data": {
                    "url": "https://th.bing.com/th/id/OIP.ZTTJgCn_iXE4sM52RK2x7gAAAA?rs=1&pid=ImgDetMain"
                },
            },
        ],
    )

    # Renderer.render(messages, HTMLRenderer()).export("测试") # type: ignore
    Renderer.render(messages, DocxRenderer()).export("测试")
    raise
