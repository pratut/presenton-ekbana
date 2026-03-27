from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from models.usage_cost import UsageCostItem, UsageCostSummary

# Prices are USD and intentionally centralized for easy updates.
# Token prices are per 1K tokens.
LLM_PRICING: Dict[str, Dict[str, Dict[str, float]]] = {
    "openai": {
        "gpt-5": {"input_per_1k": 0.00125, "output_per_1k": 0.01},
        "gpt-5-mini": {"input_per_1k": 0.00025, "output_per_1k": 0.002},
        "gpt-5-nano": {"input_per_1k": 0.00005, "output_per_1k": 0.0004},
        "gpt-4.1": {"input_per_1k": 0.002, "output_per_1k": 0.008},
        "gpt-4.1-mini": {"input_per_1k": 0.0004, "output_per_1k": 0.0016},
        "gpt-4o": {"input_per_1k": 0.0025, "output_per_1k": 0.01},
        "gpt-4o-mini": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
    "anthropic": {
        "claude-opus": {"input_per_1k": 0.015, "output_per_1k": 0.075},
        "claude-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
        "claude-haiku": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
    "google": {
        "gemini-2.5-pro": {"input_per_1k": 0.00125, "output_per_1k": 0.005},
        "gemini-2.5-flash": {"input_per_1k": 0.0003, "output_per_1k": 0.0025},
        "gemini-2.0-flash": {"input_per_1k": 0.0001, "output_per_1k": 0.0004},
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
    "ollama": {
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
    "custom": {
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
    "codex": {
        "default": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    },
}

# Prices are USD per generated image.
IMAGE_PRICING: Dict[str, Dict[str, float]] = {
    "openai": {
        "dall-e-3": 0.04,
        "gpt-image-1.5": 0.04,
        "default": 0.0,
    },
    "google": {
        "gemini-2.5-flash-image-preview": 0.0,
        "gemini-3-pro-image-preview": 0.0,
        "default": 0.0,
    },
    "pexels": {"default": 0.0},
    "pixabay": {"default": 0.0},
    "comfyui": {"default": 0.0},
}


@dataclass
class UsageCollector:
    items: list[UsageCostItem] = field(default_factory=list)

    def add_llm_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        price = _get_llm_price(provider, model)
        input_tokens = max(0, int(input_tokens or 0))
        output_tokens = max(0, int(output_tokens or 0))
        total_tokens = (
            max(0, int(total_tokens))
            if total_tokens is not None
            else input_tokens + output_tokens
        )
        amount = ((input_tokens / 1000) * price["input_per_1k"]) + (
            (output_tokens / 1000) * price["output_per_1k"]
        )
        self.items.append(
            UsageCostItem(
                service="llm",
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                unit_price_input_per_1k=price["input_per_1k"],
                unit_price_output_per_1k=price["output_per_1k"],
                amount=round(amount, 6),
                metadata=_merge_metadata_with_context(metadata),
            )
        )

    def add_image_usage(
        self,
        provider: str,
        model: str,
        images_generated: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        images_generated = max(0, int(images_generated or 0))
        per_image = _get_image_price(provider, model)
        amount = images_generated * per_image
        self.items.append(
            UsageCostItem(
                service="image",
                provider=provider,
                model=model,
                images_generated=images_generated,
                unit_price_per_image=per_image,
                amount=round(amount, 6),
                metadata=_merge_metadata_with_context(metadata),
            )
        )

    def summary(self) -> UsageCostSummary:
        llm_items = [x for x in self.items if x.service == "llm"]
        image_items = [x for x in self.items if x.service == "image"]
        total_input_tokens = sum(x.input_tokens for x in llm_items)
        total_output_tokens = sum(x.output_tokens for x in llm_items)
        total_tokens = sum(x.total_tokens for x in llm_items)
        total_images = sum(x.images_generated for x in image_items)
        llm_amount = round(sum(x.amount for x in llm_items), 6)
        image_amount = round(sum(x.amount for x in image_items), 6)
        total_amount = round(llm_amount + image_amount, 6)

        return UsageCostSummary(
            currency="USD",
            total_amount=total_amount,
            llm_amount=llm_amount,
            image_amount=image_amount,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_tokens=total_tokens,
            total_images_generated=total_images,
            items=self.items,
        )


_USAGE_COLLECTOR: ContextVar[Optional[UsageCollector]] = ContextVar(
    "usage_collector", default=None
)
_USAGE_CONTEXT: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "usage_context", default=None
)


def start_usage_collection() -> Token:
    return _USAGE_COLLECTOR.set(UsageCollector())


def get_usage_collector() -> Optional[UsageCollector]:
    return _USAGE_COLLECTOR.get()


def stop_usage_collection(token: Token):
    _USAGE_COLLECTOR.reset(token)


def set_usage_context(**context) -> Token:
    current_context = _USAGE_CONTEXT.get() or {}
    merged_context = {**current_context, **context}
    return _USAGE_CONTEXT.set(merged_context)


def reset_usage_context(token: Token):
    _USAGE_CONTEXT.reset(token)


def _merge_metadata_with_context(
    metadata: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    usage_context = _USAGE_CONTEXT.get() or {}
    if not usage_context and not metadata:
        return None
    return {**usage_context, **(metadata or {})}


def get_usage_summary_or_default() -> UsageCostSummary:
    collector = get_usage_collector()
    return collector.summary() if collector else UsageCostSummary()


def _get_llm_price(provider: str, model: str) -> Dict[str, float]:
    provider_key = (provider or "").lower()
    model_key = (model or "").lower()
    provider_prices = LLM_PRICING.get(provider_key) or LLM_PRICING["custom"]
    for pattern, price in provider_prices.items():
        if pattern == "default":
            continue
        if model_key == pattern or model_key.startswith(pattern):
            return price
    return provider_prices.get("default", {"input_per_1k": 0.0, "output_per_1k": 0.0})


def _get_image_price(provider: str, model: str) -> float:
    provider_key = (provider or "").lower()
    model_key = (model or "").lower()
    provider_prices = IMAGE_PRICING.get(provider_key) or {"default": 0.0}
    for pattern, price in provider_prices.items():
        if pattern == "default":
            continue
        if model_key == pattern or model_key.startswith(pattern):
            return float(price)
    return float(provider_prices.get("default", 0.0))
