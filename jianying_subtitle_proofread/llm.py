from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib import error, request


class Proofreader:
    def proofread(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class FakeProofreader(Proofreader):
    output: str

    def proofread(self, prompt: str) -> str:
        return self.output


@dataclass
class SequencedFakeProofreader(Proofreader):
    outputs: List[str]
    _index: int = field(default=0, init=False)

    def proofread(self, prompt: str) -> str:
        if not self.outputs:
            raise LLMError("Sequenced fake proofreader requires at least one output")
        if self._index >= len(self.outputs):
            return self.outputs[-1]
        output = self.outputs[self._index]
        self._index += 1
        return output


@dataclass
class ProviderConfig:
    provider: str
    model: str
    api_key_env: str
    base_url: str


PROVIDER_CONFIGS: Dict[str, ProviderConfig] = {
    "qwen": ProviderConfig(
        provider="qwen",
        model="qwen-max",
        api_key_env="DASHSCOPE_API_KEY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    ),
    "deepseek": ProviderConfig(
        provider="deepseek",
        model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com/chat/completions",
    ),
    "glm": ProviderConfig(
        provider="glm",
        model="glm-4-flash",
        api_key_env="ZHIPUAI_API_KEY",
        base_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
    ),
}


class LLMError(RuntimeError):
    pass


@dataclass
class OpenAICompatibleProofreader(Proofreader):
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: int = 120

    def proofread(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"{self.provider} API error: {exc.code} {detail}")
        except error.URLError as exc:
            raise LLMError(f"{self.provider} network error: {exc}")

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise LLMError(f"{self.provider} returned unexpected response shape")


def build_proofreader(
    provider: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout_seconds: int = 120,
) -> Proofreader:
    if provider not in PROVIDER_CONFIGS:
        raise LLMError(f"Unsupported provider: {provider}")
    config = PROVIDER_CONFIGS[provider]
    resolved_key = api_key or os.getenv(config.api_key_env)
    if not resolved_key:
        raise LLMError(f"Missing API key for {provider}. Set {config.api_key_env}.")
    return OpenAICompatibleProofreader(
        provider=provider,
        model=model or config.model,
        api_key=resolved_key,
        base_url=config.base_url,
        timeout_seconds=timeout_seconds,
    )
