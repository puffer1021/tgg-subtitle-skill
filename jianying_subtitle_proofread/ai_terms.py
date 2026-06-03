from __future__ import annotations

AI_TERMS_HINTS = [
    "Claude",
    "Claude Code",
    "ChatGPT",
    "OpenAI",
    "DeepSeek",
    "Gemini",
    "GLM",
    "Kimi",
    "Qwen",
    "Tongyi Qianwen",
    "Cursor",
    "Copilot",
    "Perplexity",
    "Midjourney",
    "Runway",
    "ComfyUI",
    "LangChain",
    "Llama",
    "Mistral",
    "Anthropic",
]


def render_ai_terms_hint() -> str:
    return "、".join(AI_TERMS_HINTS)
