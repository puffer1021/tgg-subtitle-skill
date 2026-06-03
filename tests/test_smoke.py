from jianying_subtitle_proofread.models import SubtitleBlock


def test_subtitle_block_dataclass_exists():
    block = SubtitleBlock(index="1", timestamp="00:00:01,000 --> 00:00:02,000", lines=["你好"])
    assert block.lines == ["你好"]
