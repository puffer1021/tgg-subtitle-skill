from jianying_subtitle_proofread.flatten import flatten_lines, rebuild_blocks
from jianying_subtitle_proofread.srt_io import parse_srt


def test_flatten_lines_assigns_stable_sequential_ids():
    blocks = parse_srt("""1
00:00:01,000 --> 00:00:03,000
他觉得这不是一
个好的事情
""")
    flattened = flatten_lines(blocks)
    assert [line.line_id for line in flattened] == [1, 2]


def test_rebuild_blocks_replaces_only_text_lines():
    blocks = parse_srt("""1
00:00:01,000 --> 00:00:03,000
他觉得这不是一
个好的事情
""")
    flattened = flatten_lines(blocks)
    corrected = {1: "他觉得这不是", 2: "一个好的事情"}
    rebuilt = rebuild_blocks(blocks, flattened, corrected)
    assert rebuilt[0].timestamp == blocks[0].timestamp
    assert rebuilt[0].lines == ["他觉得这不是", "一个好的事情"]
