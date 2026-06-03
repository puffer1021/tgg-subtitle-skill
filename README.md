# tgg-subtitle-skill

Safe `.srt` subtitle proofreading for Jianying, Whisper, and other ASR-generated video captions.

This skill uses two independent LLM proofreading passes, validates the numbered output, merges conservatively, and rebuilds the original SRT structure. It is designed to fix text problems without breaking subtitle timing.

## What It Fixes

- ASR typos and near-sound mistakes
- AI product, company, model, and technical term misrecognition
- English capitalization and split-word errors such as `chat gpt`, `deep seek`, `work flow`, `a gent`
- Repeated speech artifacts such as `我我我觉得`, `这个这个`, `然后然后`
- Awkward adjacent-line breaks while keeping the same subtitle rows

## Safety Model

- Keeps subtitle order unchanged
- Keeps timestamps unchanged
- Keeps each subtitle block's line count unchanged
- Uses reference articles only for context and terminology, not source rewriting
- Refuses to write `.fixed.srt` when model output fails validation

## Install

```bash
git clone https://github.com/puffer1021/tgg-subtitle-skill.git
cd tgg-subtitle-skill
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Providers

The CLI calls OpenAI-compatible chat completion endpoints for these providers:

- `qwen`: set `DASHSCOPE_API_KEY`
- `deepseek`: set `DEEPSEEK_API_KEY`
- `glm`: set `ZHIPUAI_API_KEY`

You can also pass `--api-key` directly for local testing.

## Usage

```bash
tgg-subtitle-skill input.srt --provider deepseek
```

```bash
tgg-subtitle-skill input.srt --provider qwen --reference article.md
```

```bash
tgg-subtitle-skill input.srt --provider glm --model glm-4-flash --chunk-size 150
```

Outputs are written next to the input file:

```text
input.fixed.srt
input.merge-report.md
```

## As An Agent Skill

Install or copy this directory into a tool-specific skill directory, for example:

```text
~/.codex/skills/tgg-subtitle-skill/
~/.claude/skills/tgg-subtitle-skill/
```

The `SKILL.md` file defines when agents should load the skill, expected inputs, safety boundaries, and CLI usage.

## Test

```bash
python -m pytest tests -q
```

The tests use fake LLM outputs, so they do not require provider API keys.

## Package Layout

```text
tgg-subtitle-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── pyproject.toml
├── jianying_subtitle_proofread/
├── examples/
├── references/
└── tests/
```

## License

MIT
