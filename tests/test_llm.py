import os

import pytest

from jianying_subtitle_proofread.llm import LLMError, PROVIDER_CONFIGS, build_proofreader


@pytest.mark.parametrize(
    "provider,env_name",
    [
        ("qwen", "DASHSCOPE_API_KEY"),
        ("deepseek", "DEEPSEEK_API_KEY"),
        ("glm", "ZHIPUAI_API_KEY"),
    ],
)
def test_build_proofreader_uses_provider_defaults(provider, env_name, monkeypatch):
    monkeypatch.setenv(env_name, "test-key")
    tool = build_proofreader(provider)
    assert tool.model == PROVIDER_CONFIGS[provider].model
    assert tool.base_url == PROVIDER_CONFIGS[provider].base_url


def test_build_proofreader_rejects_missing_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(LLMError):
        build_proofreader("deepseek")
