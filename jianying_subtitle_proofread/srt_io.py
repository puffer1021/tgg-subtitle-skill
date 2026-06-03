from __future__ import annotations

from typing import List

from .models import SubtitleBlock


class SRTParseError(ValueError):
    pass


def parse_srt(text: str) -> List[SubtitleBlock]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        raise SRTParseError("SRT is empty")

    chunks = [chunk for chunk in normalized.split("\n\n") if chunk.strip()]
    blocks = []
    for chunk in chunks:
        lines = chunk.split("\n")
        if len(lines) < 3:
            raise SRTParseError("Each block must contain index, timestamp, and text")
        index = lines[0].strip()
        timestamp = lines[1].strip()
        body = [line.rstrip() for line in lines[2:]]
        if not index or not timestamp or not any(line != "" for line in body):
            raise SRTParseError("Invalid SRT block")
        blocks.append(SubtitleBlock(index=index, timestamp=timestamp, lines=body))
    return blocks


def serialize_srt(blocks: List[SubtitleBlock]) -> str:
    parts = []
    for block in blocks:
        if not block.index or not block.timestamp or not block.lines:
            raise SRTParseError("Cannot serialize incomplete subtitle block")
        parts.append("\n".join([block.index, block.timestamp] + block.lines))
    return "\n\n".join(parts) + "\n"
