from __future__ import annotations

from typing import Iterable

from .models import MergeDecision


def render_merge_report(decisions: Iterable[MergeDecision]) -> str:
    lines = ["# Merge Report", ""]
    for decision in decisions:
        lines.extend(
            [
                f"## Line {decision.line_id}",
                f"- A: {decision.candidate_a}",
                f"- B: {decision.candidate_b}",
                f"- Chosen: {decision.chosen_text}",
                f"- Source: {decision.source}",
                f"- Reason: {decision.reason}",
                "",
            ]
        )
    return "\n".join(lines)
