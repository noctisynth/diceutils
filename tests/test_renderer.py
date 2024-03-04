from diceutils.renderer import Renderer, Messages, Role
from diceutils.renderer.html import HTMLRenderer


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
        {"type": "image", "data": {"url": "http://a.com/2.png"}},
    ]
    msg_content_3 = [
        {
            "type": "text",
            "data": {
                "text": ".rd10*5"
            }
        }
    ]
    msg_content_4 = [
         {
            "type": "text",
            "data": {
                "text": "[苏向夜]掷骰: 1D10*5={10}*5=50"
            }
        }
    ]
    messages.add_message("230234235", Role.GM, "苏向夜", "date", msg_content_1)
    messages.add_message("130324324", Role.PL, "少年狐", "date", msg_content_1)
    messages.add_message("120232412", Role.PL, "Aruvelut", "date", msg_content_2)
    messages.add_message("230234235", Role.GM, "苏向夜", "date", msg_content_3)
    messages.add_message("3371047314", Role.DICER, "骰娘", "date", msg_content_4)
    messages.add_message(
        "130232542",
        Role.OB,
        "简律纯",
        "datetime.datetime.now()",
        [
            {"type": "text", "data": {"text": "谴责！"}},
        ],
    )

    renderer = Renderer.render(messages, HTMLRenderer())
    renderer.export("测试")