from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .flatten import flatten_lines, rebuild_blocks
from .llm import LLMError, FakeProofreader, SequencedFakeProofreader, build_proofreader
from .merge import merge_candidates
from .prompting import build_proofread_prompt, build_reference_clean_prompt, build_retry_prompt
from .reporting import render_merge_report
from .srt_io import parse_srt, serialize_srt
from .validation import ValidationError, parse_numbered_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("--reference")
    parser.add_argument("--provider", choices=["qwen", "deepseek", "glm"])
    parser.add_argument("--model")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--chunk-size", type=int, default=80)
    parser.add_argument("--fake-output-a")
    parser.add_argument("--fake-output-b")
    parser.add_argument("--fake-output")
    parser.add_argument("--fake-output-a-file")
    parser.add_argument("--fake-output-b-file")
    parser.add_argument("--fake-output-file")
    parser.add_argument("--fake-output-separator", default="\n===CHUNK===\n")
    parser.add_argument("--fake-retry-same-output", action="store_true")
    return parser


def _load_fake_outputs(inline_text: Optional[str], file_path: Optional[str], separator: str) -> Optional[List[str]]:
    raw = inline_text
    if file_path:
        raw = Path(file_path).read_text(encoding="utf-8")
    if raw is None:
        return None
    return raw.split(separator) if separator in raw else [raw]


def _build_fake_proofreader(outputs: List[str], reuse_for_retry: bool):
    if len(outputs) == 1:
        return FakeProofreader(outputs[0])
    if reuse_for_retry:
        expanded: List[str] = []
        for output in outputs:
            expanded.extend([output, output])
        return SequencedFakeProofreader(expanded)
    return SequencedFakeProofreader(outputs)


def _build_pass_proofreaders(args: argparse.Namespace):
    fake_a_outputs = _load_fake_outputs(args.fake_output_a or args.fake_output, args.fake_output_a_file or args.fake_output_file, args.fake_output_separator)
    fake_b_outputs = _load_fake_outputs(args.fake_output_b or args.fake_output, args.fake_output_b_file or args.fake_output_file, args.fake_output_separator)
    if fake_a_outputs and fake_b_outputs:
        return (
            _build_fake_proofreader(fake_a_outputs, args.fake_retry_same_output),
            _build_fake_proofreader(fake_b_outputs, args.fake_retry_same_output),
        )
    if not args.provider:
        raise ValueError("Provide --provider for real LLM calls, or fake outputs for tests")
    proofreader = build_proofreader(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        timeout_seconds=args.timeout,
    )
    return proofreader, proofreader


def _run_pass_with_retry(proofreader, prompt: str, expected_ids: List[int]) -> Tuple[dict, str]:
    first_output = proofreader.proofread(prompt)
    parsed = parse_numbered_output(first_output, expected_ids)
    retry_prompt = build_retry_prompt(prompt, first_output)
    retry_output = proofreader.proofread(retry_prompt)
    try:
        retry_parsed = parse_numbered_output(retry_output, expected_ids)
        return retry_parsed, retry_output
    except ValidationError:
        return parsed, first_output


def _proofread_in_chunks(flattened, reference_text, proofreader, pass_name: str, chunk_size: int = 80) -> Dict[int, str]:
    corrected: Dict[int, str] = {}
    total_chunks = math.ceil(len(flattened) / chunk_size)
    for chunk_index in range(total_chunks):
        start = chunk_index * chunk_size
        chunk = flattened[start:start + chunk_size]
        expected_ids = [line.line_id for line in chunk]
        prompt = build_proofread_prompt(chunk, reference_text=reference_text, pass_name=pass_name)
        parsed, _ = _run_pass_with_retry(proofreader, prompt, expected_ids)
        for line_id, text in parsed.items():
            corrected[line_id] = text
    return corrected


def run(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input_path)
    reference_text = Path(args.reference).read_text(encoding="utf-8") if args.reference else None
    original_text = input_path.read_text(encoding="utf-8")
    blocks = parse_srt(original_text)
    flattened = flatten_lines(blocks)

    try:
        proofreader_a, proofreader_b = _build_pass_proofreaders(args)
    except (ValueError, LLMError):
        return 1

    # 预处理：用 LLM 将原始文稿整理成逻辑通顺的干净正文，仅调用一次
    if reference_text:
        try:
            clean_prompt = build_reference_clean_prompt(reference_text)
            reference_text = proofreader_a.proofread(clean_prompt)
        except (LLMError, Exception):
            pass  # 清洗失败则降级使用原始文稿

    try:
        candidate_a = _proofread_in_chunks(flattened, reference_text, proofreader_a, pass_name="A", chunk_size=args.chunk_size)
        candidate_b = _proofread_in_chunks(flattened, reference_text, proofreader_b, pass_name="B", chunk_size=args.chunk_size)
    except (ValidationError, LLMError):
        return 1

    merged, decisions = merge_candidates(candidate_a, candidate_b, reference_text=reference_text)
    rebuilt = rebuild_blocks(blocks, flattened, merged)

    output_path = input_path.with_suffix(".fixed.srt")
    report_path = input_path.with_suffix(".merge-report.md")
    output_path.write_text(serialize_srt(rebuilt), encoding="utf-8")
    report_path.write_text(render_merge_report(decisions), encoding="utf-8")
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
