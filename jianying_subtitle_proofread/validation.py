from __future__ import annotations

import re
from typing import Dict, Iterable, List


class ValidationError(ValueError):
    pass


LINE_RE = re.compile(r"^\[(\d+)\]\s?(.*)$")


def _normalize_ids(parsed: Dict[int, str], expected_list: List[int]) -> Dict[int, str]:
    parsed_keys = sorted(parsed.keys())
    if parsed_keys == sorted(expected_list):
        return parsed
    if len(parsed_keys) != len(expected_list):
        raise ValidationError("Output ids do not match expected ids")

    expected_first = min(expected_list)
    parsed_first = parsed_keys[0]
    offset = parsed_first - expected_first
    remapped = {line_id - offset: text for line_id, text in parsed.items()}
    if sorted(remapped.keys()) != sorted(expected_list):
        raise ValidationError("Output ids do not match expected ids")
    return remapped


def parse_numbered_output(text: str, expected_ids: Iterable[int]) -> Dict[int, str]:
    expected_list = list(expected_ids)
    parsed: Dict[int, str] = {}
    raw_lines = [line for line in text.replace("\r\n", "\n").split("\n") if line != ""]
    for raw_line in raw_lines:
        match = LINE_RE.match(raw_line)
        if not match:
            raise ValidationError("Output contains non-numbered content")
        line_id = int(match.group(1))
        if line_id in parsed:
            raise ValidationError("Duplicate line id in output")
        parsed[line_id] = match.group(2)

    return _normalize_ids(parsed, expected_list)


def expected_ids_from_count(count: int) -> List[int]:
    return list(range(1, count + 1))
