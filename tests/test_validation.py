import pytest

from jianying_subtitle_proofread.prompting import build_proofread_prompt, build_retry_prompt
from jianying_subtitle_proofread.srt_io import parse_srt
from jianying_subtitle_proofread.flatten import flatten_lines
from jianying_subtitle_proofread.validation import ValidationError, parse_numbered_output


def test_parse_numbered_output_accepts_exact_numbered_lines():
    parsed = parse_numbered_output("[1] 他觉得这不是\n[2] 一个好的事情", expected_ids=[1, 2])
    assert parsed == {1: "他觉得这不是", 2: "一个好的事情"}


def test_parse_numbered_output_rejects_missing_ids():
    with pytest.raises(ValidationError):
        parse_numbered_output("[1] 他觉得这不是", expected_ids=[1, 2])


def test_parse_numbered_output_rejects_extra_explanation():
    with pytest.raises(ValidationError):
        parse_numbered_output("这里是说明\n[1] A\n[2] B", expected_ids=[1, 2])


def test_parse_numbered_output_accepts_chunk_global_ids_and_remaps_to_local_ids():
    parsed = parse_numbered_output("[81] 哈哈\n[82] 你看起来是我们这最老的", expected_ids=[1, 2])
    assert parsed == {1: "哈哈", 2: "你看起来是我们这最老的"}


def test_build_prompt_can_include_reference_context_and_ai_terms():
    blocks = parse_srt("""1
00:00:01,000 --> 00:00:03,000
你好世界
""")
    prompt = build_proofread_prompt(flatten_lines(blocks), reference_text="这是一篇参考文章", pass_name="A")
    assert "参考文章" in prompt
    assert "你好世界" in prompt
    assert "不要随意新增标点" in prompt
    assert "不要为了规范专有名词而过度给整句中文新增空格" in prompt
    assert "Claude Code" in prompt
    assert "DeepSeek" in prompt


def test_build_retry_prompt_mentions_retry_focus():
    prompt = build_retry_prompt("原始prompt", "[1] 原输出")
    assert "AI 专有名词误识别" in prompt
    assert "重复词未清理" in prompt
    assert "不要随意新增标点" in prompt
    assert "不要为了规范专有名词而给整句中文过度加空格" in prompt
    assert "[1] 原输出" in prompt
