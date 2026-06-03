from pathlib import Path

from jianying_subtitle_proofread.srt_io import parse_srt


def test_coverage_dataset_exists_and_is_parseable():
    path = Path(__file__).parent / "fixtures" / "coverage_full_input.srt"
    text = path.read_text(encoding="utf-8")
    blocks = parse_srt(text)
    assert len(blocks) == 92


def test_coverage_dataset_covers_core_error_families():
    path = Path(__file__).parent / "fixtures" / "coverage_full_input.srt"
    text = path.read_text(encoding="utf-8")

    expected_fragments = [
        "hello大家好",
        "cloud code",
        "gimini",
        "chat gpt",
        "deep seek",
        "我我我觉得",
        "这个这个产品",
        "然后然后",
        "它它它",
        "cursor",
        "claud",
        "gemni",
        "agent",
        "work flow",
        "a gent",
        "multi agent",
        "rag",
        "demo",
        "copilot",
        "chatbot",
        "mcp",
        "model context protocol",
        "open ai",
        "anthorpic",
        "kimi k2",
        "qwen",
        "glm",
        "tongyi qianwen",
        "public city",
        "mid journey",
        "run way",
        "comfy ui",
        "lang chain",
        "lama",
        "mistal",
    ]

    for fragment in expected_fragments:
        assert fragment in text
