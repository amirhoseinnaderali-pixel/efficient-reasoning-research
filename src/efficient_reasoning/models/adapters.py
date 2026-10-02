from __future__ import annotations

import json
import os
import time
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

from ..core import GenerationResult


class BaseModelAdapter(ABC):
    provider = "unknown"

    def __init__(self, model: str, **kwargs: Any) -> None:
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.2,
        timeout_seconds: float = 120.0,
        seed: int | None = None,
        top_p: float = 1.0,
    ) -> GenerationResult:
        raise NotImplementedError


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=max(0.1, float(timeout))) as resp:
        return json.loads(resp.read().decode())


class MockAdapter(BaseModelAdapter):
    provider = "mock"

    def __init__(self, model: str = "mock-coder", **kwargs: Any) -> None:
        super().__init__(model, **kwargs)
        self.calls = 0

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, timeout_seconds: float = 120.0, seed: int | None = None, top_p: float = 1.0) -> GenerationResult:
        del max_tokens, timeout_seconds
        self.calls += 1
        task = self.config.get("task_id", "")
        code = {
            "add_two_numbers": "def add_two_numbers(a, b):\n    return a + b",
            "is_palindrome": "def is_palindrome(s):\n    return s == s[::-1]",
            "count_vowels": "def count_vowels(s):\n    return sum(1 for ch in s if ch.lower() in 'aeiou')",
            "max_subarray": "def max_subarray(nums):\n    best = cur = nums[0]\n    for x in nums[1:]:\n        cur = max(x, cur + x)\n        best = max(best, cur)\n    return best",
            "two_sum": "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]",
        }.get(task, "def answer(*args):\n    return None")
        if self.config.get("make_first_wrong") and self.calls == 1 and task == "add_two_numbers":
            code = "def add_two_numbers(a, b):\n    return a - b"
        return GenerationResult(
            code,
            self.model,
            input_tokens=len(prompt.split()),
            output_tokens=len(code.split()),
            metadata={"provider": self.provider, "usage_reported": True, "seed_enforced": True, "generation_parameters": {"temperature": temperature, "seed": seed, "top_p": top_p}},
        )


class OpenAICompatibleAdapter(BaseModelAdapter):
    provider = "openai_compatible"

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, timeout_seconds: float = 120.0, seed: int | None = None, top_p: float = 1.0) -> GenerationResult:
        base = self.config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is required")
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        seed_supported = bool(self.config.get("supports_seed", True))
        if seed is not None and seed_supported:
            payload["seed"] = seed
        t = time.perf_counter()
        data = _post_json(base + "/chat/completions", payload, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, timeout_seconds)
        dt = time.perf_counter() - t
        usage = data.get("usage", {})
        return GenerationResult(
            data["choices"][0]["message"]["content"],
            self.model,
            int(usage.get("prompt_tokens", 0) or 0),
            int(usage.get("completion_tokens", 0) or 0),
            dt,
            metadata={"provider": self.provider, "usage_reported": "prompt_tokens" in usage and "completion_tokens" in usage, "seed_enforced": seed is not None and seed_supported, "generation_parameters": {"temperature": temperature, "seed": seed if seed_supported else None, "top_p": top_p}},
        )


class OllamaAdapter(BaseModelAdapter):
    provider = "ollama"

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, timeout_seconds: float = 120.0, seed: int | None = None, top_p: float = 1.0) -> GenerationResult:
        base = self.config.get("base_url", "http://localhost:11434").rstrip("/")
        options: dict[str, Any] = {"temperature": temperature, "num_predict": max_tokens, "top_p": top_p}
        seed_supported = bool(self.config.get("supports_seed", True))
        if seed is not None and seed_supported:
            options["seed"] = seed
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False, "options": options}
        t = time.perf_counter()
        data = _post_json(base + "/api/chat", payload, {"Content-Type": "application/json"}, timeout_seconds)
        dt = time.perf_counter() - t
        return GenerationResult(
            data.get("message", {}).get("content", ""),
            self.model,
            int(data.get("prompt_eval_count") or 0),
            int(data.get("eval_count") or 0),
            dt,
            metadata={"provider": self.provider, "usage_reported": "prompt_eval_count" in data and "eval_count" in data, "seed_enforced": seed is not None and seed_supported, "generation_parameters": {"temperature": temperature, "seed": seed if seed_supported else None, "top_p": top_p}},
        )


class GoogleAdapter(BaseModelAdapter):
    provider = "google"

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2, timeout_seconds: float = 120.0, seed: int | None = None, top_p: float = 1.0) -> GenerationResult:
        key = self.config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY is required")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={key}"
        gen: dict[str, Any] = {"maxOutputTokens": max_tokens, "temperature": temperature, "topP": top_p}
        seed_supported = bool(self.config.get("supports_seed", False))
        if seed is not None and seed_supported:
            gen["seed"] = seed
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": gen}
        t = time.perf_counter()
        data = _post_json(url, payload, {"Content-Type": "application/json"}, timeout_seconds)
        dt = time.perf_counter() - t
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        usage = data.get("usageMetadata", {})
        return GenerationResult(
            text,
            self.model,
            int(usage.get("promptTokenCount") or 0),
            int(usage.get("candidatesTokenCount") or 0),
            dt,
            metadata={"provider": self.provider, "usage_reported": "promptTokenCount" in usage and "candidatesTokenCount" in usage, "seed_enforced": seed is not None and seed_supported, "generation_parameters": {"temperature": temperature, "seed": seed if seed_supported else None, "top_p": top_p}},
        )
