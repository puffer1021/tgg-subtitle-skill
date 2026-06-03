from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .models import MergeDecision


PUNCTUATION = "，。！？；：,.!?;:"


def _normalize(text: str) -> str:
    return text.strip().lower()


def _strip_trailing_punctuation(text: str) -> str:
    return text.rstrip(PUNCTUATION).rstrip()


def _is_punctuation_only_change(original: str, candidate: str) -> bool:
    return _strip_trailing_punctuation(original) == _strip_trailing_punctuation(candidate) and original != candidate


def merge_candidates(
    candidate_a: Dict[int, str],
    candidate_b: Dict[int, str],
    reference_text: Optional[str] = None,
) -> Tuple[Dict[int, str], List[MergeDecision]]:
    merged: Dict[int, str] = {}
    decisions: List[MergeDecision] = []
    reference_text = reference_text or ""

    for line_id in sorted(candidate_a.keys()):
        text_a = candidate_a[line_id]
        text_b = candidate_b[line_id]
        if text_a == text_b:
            merged[line_id] = text_a
            decisions.append(MergeDecision(line_id, text_a, "both", "A/B 一致", text_a, text_b, bool(reference_text)))
            continue

        source = "A"
        chosen = text_a
        reason = "默认采用 A，因两轮冲突且未命中更强规则"

        if _is_punctuation_only_change(text_a, text_b):
            source, chosen, reason = "A", text_a, "仅有标点差异，默认不新增标点"
        elif _is_punctuation_only_change(text_b, text_a):
            source, chosen, reason = "B", text_b, "仅有标点差异，默认不新增标点"
        elif reference_text:
            a_in_ref = _normalize(text_a) in _normalize(reference_text)
            b_in_ref = _normalize(text_b) in _normalize(reference_text)
            if a_in_ref and not b_in_ref:
                source, chosen, reason = "A", text_a, "A 更符合参考文章中的专有名词或上下文"
            elif b_in_ref and not a_in_ref:
                source, chosen, reason = "B", text_b, "B 更符合参考文章中的专有名词或上下文"
        if chosen == text_a and reason == "默认采用 A，因两轮冲突且未命中更强规则" and len(text_b) < len(text_a):
            source, chosen, reason = "B", text_b, "B 改动更保守"

        merged[line_id] = chosen
        decisions.append(MergeDecision(line_id, chosen, source, reason, text_a, text_b, bool(reference_text)))
    return merged, decisions
