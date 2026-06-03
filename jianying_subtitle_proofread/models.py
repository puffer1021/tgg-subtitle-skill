from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SubtitleBlock:
    index: str
    timestamp: str
    lines: List[str]


@dataclass
class FlattenedLine:
    line_id: int
    block_index: int
    line_index: int
    text: str


@dataclass
class MergeDecision:
    line_id: int
    chosen_text: str
    source: str
    reason: str
    candidate_a: str
    candidate_b: str
    reference_used: bool = False
    note: Optional[str] = None
