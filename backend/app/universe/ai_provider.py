# GEO Universe AI Provider Interface
# Unified adapter layer for all AI model providers.
# Supports: OpenAI GPT, Anthropic Claude, Google Gemini, DeepSeek, etc.
# All Agent plugins go through this interface instead of calling APIs directly.

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from functools import lru_cache
import os
import yaml


_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_PROVIDERS_PATH = os.path.join(_PROJECT_ROOT, "config", "universe", "providers.yaml")


@dataclass
class ChatMessage:
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


@dataclass
class ChatCompletionRequest:
    messages: List[ChatMessage]
    model: str = ""
    temperature: float = 0.3
    max_tokens: int = 2000
    tools: Optional[List[Dict]] = None
    stop: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatCompletionResponse:
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    tool_calls: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---- Base Provider Interface ----

class BaseAIProvider(ABC):
    provider_id: str = ""
    provider_name: str = ""
    default_model: str = ""

    @abstractmethod
    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        ...

    @abstractmethod
    def list_models(self) -> List[str]:
        ...

    def validate_config(self) -> bool:
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "supports_tools": False,
            "supports_streaming": False,
            "supports_vision": False,
            "max_context_tokens": 4096,
        }


# ---- OpenAI Provider ----

class OpenAIProvider(BaseAIProvider):
    provider_id = "openai"
    provider_name = "OpenAI"
    default_model = "gpt-4o"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        model = request.model or self.default_model
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            choice = resp.choices[0]
            return ChatCompletionResponse(
                content=choice.message.content or "",
                model=resp.model,
                usage={"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens},
                finish_reason=choice.finish_reason or "stop",
            )
        except ImportError:
            return ChatCompletionResponse(
                content=f"[OpenAI not configured] Model: {model}",
                model=model,
            )

    def list_models(self) -> List[str]:
        return [self.default_model, "gpt-4-turbo", "gpt-3.5-turbo"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "supports_tools": True,
            "supports_streaming": True,
            "supports_vision": True,
            "max_context_tokens": 128000,
        }


# ---- Claude Provider ----

class ClaudeProvider(BaseAIProvider):
    provider_id = "claude"
    provider_name = "Anthropic Claude"
    default_model = "claude-sonnet-4-20250514"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        model = request.model or self.default_model
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            system_msg = ""
            messages = []
            for m in request.messages:
                if m.role == "system":
                    system_msg += m.content
                else:
                    messages.append({"role": m.role, "content": m.content})
            kwargs = {"model": model, "messages": messages, "max_tokens": request.max_tokens}
            if system_msg:
                kwargs["system"] = system_msg
            resp = await client.messages.create(**kwargs)
            return ChatCompletionResponse(
                content=resp.content[0].text if resp.content else "",
                model=resp.model,
                usage={"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
            )
        except ImportError:
            return ChatCompletionResponse(
                content=f"[Claude not configured] Model: {model}",
                model=model,
            )

    def list_models(self) -> List[str]:
        return [self.default_model, "claude-opus-4-20250514", "claude-haiku-3-5"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "supports_tools": True,
            "supports_streaming": True,
            "supports_vision": True,
            "max_context_tokens": 200000,
        }


# ---- Gemini Provider ----

class GeminiProvider(BaseAIProvider):
    provider_id = "gemini"
    provider_name = "Google Gemini"
    default_model = "gemini-2.5-pro"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        model = request.model or self.default_model
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            gm = genai.GenerativeModel(model)
            prompt = "\n".join([f"{m.role}: {m.content}" for m in request.messages])
            resp = await gm.generate_content_async(prompt)
            return ChatCompletionResponse(
                content=resp.text or "",
                model=model,
            )
        except ImportError:
            return ChatCompletionResponse(
                content=f"[Gemini not configured] Model: {model}",
                model=model,
            )

    def list_models(self) -> List[str]:
        return [self.default_model, "gemini-2.5-flash"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "supports_tools": True,
            "supports_streaming": True,
            "supports_vision": True,
            "max_context_tokens": 1048576,
        }


# ---- DeepSeek Provider ----

class DeepSeekProvider(BaseAIProvider):
    provider_id = "deepseek"
    provider_name = "DeepSeek"
    default_model = "deepseek-chat"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")

    async def chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        model = request.model or self.default_model
        try:
            import openai
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            choice = resp.choices[0]
            return ChatCompletionResponse(
                content=choice.message.content or "",
                model=resp.model,
                usage={"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens},
            )
        except ImportError:
            return ChatCompletionResponse(
                content=f"[DeepSeek not configured] Model: {model}",
                model=model,
            )

    def list_models(self) -> List[str]:
        return [self.default_model, "deepseek-reasoner"]


# ---- Provider Registry ----

class AIProviderRegistry:
    _instance = None

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _PROVIDERS_PATH
        self._providers: Dict[str, BaseAIProvider] = {}
        self._default_provider: str = ""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            self._default_provider = raw.get("default_provider", "")
            for pid, cfg in raw.get("providers", {}).items():
                if cfg.get("enabled", True):
                    self._register_builtin(pid, cfg)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _register_builtin(self, pid: str, cfg: Dict):
        provider_map = {
            "openai": OpenAIProvider,
            "claude": ClaudeProvider,
            "gemini": GeminiProvider,
            "deepseek": DeepSeekProvider,
        }
        if pid in provider_map:
            self._providers[pid] = provider_map[pid](cfg)

    def register(self, provider_id: str, provider: BaseAIProvider):
        self._providers[provider_id] = provider

    def get(self, provider_id: str = "") -> Optional[BaseAIProvider]:
        if not provider_id:
            provider_id = self._default_provider
        return self._providers.get(provider_id)

    def get_default(self) -> Optional[BaseAIProvider]:
        return self.get(self._default_provider) or (list(self._providers.values())[0] if self._providers else None)

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": pid,
                "name": p.provider_name,
                "default_model": p.default_model,
                "capabilities": p.get_capabilities(),
            }
            for pid, p in self._providers.items()
        ]

    def export_full(self) -> Dict[str, Any]:
        return {
            "default_provider": self._default_provider,
            "providers": self.list_providers(),
        }


@lru_cache()
def get_ai_provider_registry() -> AIProviderRegistry:
    return AIProviderRegistry.get_instance()
