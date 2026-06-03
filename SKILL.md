---
name: puffer1021-subtitle-proofreader
description: Use when proofreading Jianying, Whisper, or other video .srt subtitles while preserving timestamps, subtitle order, and per-block line counts.
version: 0.1.0
author: puffer1021
category: creative
tags:
  - subtitles
  - srt
  - proofreading
  - captions
  - video
platforms:
  - CODEX_CLI
  - CLAUDE_CODE
permissions:
  - filesystem
  - network
  - shell
---

# puffer1021-subtitle-proofreader

Use this skill when the user provides a Jianying, Whisper, or other video `.srt` subtitle file and wants safe proofreading without changing timestamps or subtitle structure.

## Inputs

- Required: `.srt` subtitle file
- Optional: reference article for background understanding only
- Optional: provider choice, supports `qwen`, `deepseek`, `glm`

## Outputs

- `*.fixed.srt`
- `*.merge-report.md`

## Safety boundary

- Keep subtitle order unchanged
- Keep timestamps unchanged
- Keep per-block line counts unchanged
- Reference article is background-only, not rewrite source
- If provider output fails validation, do not write `.fixed.srt`

## Workflow

1. Parse the `.srt` file and flatten subtitle text lines into stable numbered rows.
2. Run two independent proofreading passes in chunks.
3. Validate that model output contains exactly the expected numbered rows.
4. Conservatively merge A/B candidates, preferring agreement and avoiding punctuation-only rewrites.
5. Rebuild the original SRT structure with corrected text only.
6. Write `*.fixed.srt` and `*.merge-report.md` next to the input file.

## Provider selection

- Natural language is allowed, for example: “用 deepseek 跑这份字幕”
- CLI also supports explicit selection with `--provider`
- Optional model override with `--model`
- Environment variables: `DASHSCOPE_API_KEY` for qwen, `DEEPSEEK_API_KEY` for deepseek, `ZHIPUAI_API_KEY` for glm.

## CLI examples

```bash
tgg-subtitle-skill input.srt --provider qwen --reference article.md
```

```bash
tgg-subtitle-skill input.srt --provider glm --model glm-4-flash --reference article.md
```

```bash
tgg-subtitle-skill input.srt --provider deepseek --chunk-size 150
```

## Setup if the CLI is unavailable

If `tgg-subtitle-skill` is not installed, install the public package:

```bash
python3 -m pip install git+https://github.com/puffer1021/tgg-subtitle-skill.git
```

Then rerun the CLI command. Do not proceed with a fake output unless the user explicitly asks for a dry run or test mode.

## Package layout

- `SKILL.md`: trigger, inputs, outputs, safety boundary
- `README.md`: implementation and engineering notes
- `jianying_subtitle_proofread/`: Python implementation
- `examples/`: example input and output files
- `tests/fixtures/`: test-only subtitle datasets
- `references/`: optional terminology and workflow notes
