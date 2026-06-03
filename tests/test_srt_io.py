from jianying_subtitle_proofread.srt_io import parse_srt, serialize_srt

SRT_TEXT = """1
00:00:01,000 --> 00:00:03,000
他觉得这不是一
个好的事情

2
00:00:03,500 --> 00:00:05,000
we should go to beijing
"""


def test_parse_srt_preserves_blocks_and_line_counts():
    blocks = parse_srt(SRT_TEXT)
    assert [b.index for b in blocks] == ["1", "2"]
    assert blocks[0].lines == ["他觉得这不是一", "个好的事情"]


def test_serialize_srt_round_trips_structure():
    blocks = parse_srt(SRT_TEXT)
    assert serialize_srt(blocks).strip() == SRT_TEXT.strip()
