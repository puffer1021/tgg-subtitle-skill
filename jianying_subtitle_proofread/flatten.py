from __future__ import annotations

from typing import Dict, List

from .models import FlattenedLine, SubtitleBlock


def flatten_lines(blocks: List[SubtitleBlock]) -> List[FlattenedLine]:
    flattened = []
    next_id = 1
    for block_index, block in enumerate(blocks):
        for line_index, line in enumerate(block.lines):
            flattened.append(
                FlattenedLine(
                    line_id=next_id,
                    block_index=block_index,
                    line_index=line_index,
                    text=line,
                )
            )
            next_id += 1
    return flattened


def rebuild_blocks(
    blocks: List[SubtitleBlock],
    flattened: List[FlattenedLine],
    corrected: Dict[int, str],
) -> List[SubtitleBlock]:
    rebuilt = [SubtitleBlock(index=block.index, timestamp=block.timestamp, lines=list(block.lines)) for block in blocks]
    for item in flattened:
        rebuilt[item.block_index].lines[item.line_index] = corrected[item.line_id]
    return rebuilt
