from diceutils.renderer import Renderer, Messages, Role


def test_render():
    messages = Messages()
    msg_content_1 = [
        {"type": "text", "data": {"text": "“你好”，PC顿了顿道，“非常好”"}},
        {"type": "image", "data": {"url": "http://a.com/1.png"}},
    ]
    msg_content_2 = [
        {
            "type": "text",
            "data": {
                "text": "男人最终还是跟了上来，只是嘴里连连念叨着:“我是美国公民，我是美国公民……”"
            },
        },
        {"type": "image", "data": {"url": "http://a.com/2.png"}},
    ]
    messages.add_message(
        "1302425", Role.PL, "张三", "datetime.datetime.now()", msg_content_1
    )
    messages.add_message(
        "1302425", Role.PL, "张三", "datetime.datetime.now()", msg_content_2
    )

    # renderer = Renderer.render(messages, DocxRenderer())
    # renderer.export()
