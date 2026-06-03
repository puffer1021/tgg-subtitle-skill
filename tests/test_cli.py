from pathlib import Path

from jianying_subtitle_proofread.cli import build_parser, run
from jianying_subtitle_proofread.llm import FakeProofreader, SequencedFakeProofreader


def test_fake_proofreader_returns_configured_output():
    tool = FakeProofreader("[1] A\n[2] B")
    assert tool.proofread("ignored") == "[1] A\n[2] B"


def test_sequenced_fake_proofreader_returns_outputs_in_order():
    tool = SequencedFakeProofreader(["[1] A", "[1] B"])
    assert tool.proofread("ignored") == "[1] A"
    assert tool.proofread("ignored") == "[1] B"
    assert tool.proofread("ignored") == "[1] B"


def test_parser_accepts_provider_and_model():
    args = build_parser().parse_args(["input.srt", "--provider", "qwen", "--model", "qwen-plus"])
    assert args.provider == "qwen"
    assert args.model == "qwen-plus"


def test_parser_accepts_chunked_fake_output_options():
    args = build_parser().parse_args(["input.srt", "--fake-output-a-file", "a.txt", "--fake-output-b-file", "b.txt", "--fake-retry-same-output"])
    assert args.fake_output_a_file == "a.txt"
    assert args.fake_output_b_file == "b.txt"
    assert args.fake_retry_same_output is True


def test_run_writes_fixed_srt_and_merge_report(tmp_path: Path):
    input_path = tmp_path / "input.srt"
    input_path.write_text(
        """1
00:00:01,000 --> 00:00:03,000
他觉得这不是一
个好的事情
""",
        encoding="utf-8",
    )
    result = run([
        str(input_path),
        "--fake-output-a",
        "[1] 他觉得这不是\n[2] 一个好的事情",
        "--fake-output-b",
        "[1] 他觉得这不是\n[2] 一个好的事情",
    ])
    output = tmp_path / "input.fixed.srt"
    report = tmp_path / "input.merge-report.md"
    assert result == 0
    assert output.exists()
    assert report.exists()
    assert "他觉得这不是\n一个好的事情" in output.read_text(encoding="utf-8")


def test_run_refuses_to_write_when_output_ids_are_invalid(tmp_path: Path):
    input_path = tmp_path / "input.srt"
    input_path.write_text(
        """1
00:00:01,000 --> 00:00:03,000
Hello
world
""",
        encoding="utf-8",
    )
    result = run([
        str(input_path),
        "--fake-output-a",
        "[1] Hello",
        "--fake-output-b",
        "[1] Hello\n[2] world",
    ])
    assert result == 1
    assert not (tmp_path / "input.fixed.srt").exists()


def test_run_requires_provider_or_fake_outputs(tmp_path: Path):
    input_path = tmp_path / "input.srt"
    input_path.write_text(
        """1
00:00:01,000 --> 00:00:03,000
Hello
""",
        encoding="utf-8",
    )
    result = run([str(input_path)])
    assert result == 1


def test_run_supports_chunked_global_ids(tmp_path: Path, monkeypatch):
    input_path = tmp_path / "input.srt"
    input_path.write_text(
        """1
00:00:01,000 --> 00:00:03,000
Hello

2
00:00:03,000 --> 00:00:05,000
world
""",
        encoding="utf-8",
    )

    from jianying_subtitle_proofread import cli

    cli._proofread_in_chunks(
        [type('L', (), {'line_id': 1, 'text': 'Hello'})(), type('L', (), {'line_id': 2, 'text': 'world'})()],
        None,
        FakeProofreader("[11] Hello\n[12] world"),
        pass_name="A",
        chunk_size=2,
    )
