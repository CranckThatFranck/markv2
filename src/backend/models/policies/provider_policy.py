"""Politica de providers do Mark Core v2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProviderPolicyDecision:
    provider: str
    allowed: bool
    reason: str | None = None


class ProviderPolicy:
    """Valida provider ativo e politica de fallback entre providers."""

    def __init__(self, allow_cross_provider_fallback: bool = False) -> None:
        self.allow_cross_provider_fallback = allow_cross_provider_fallback
        self.allowed_providers = {"google_ai", "vertex_ai"}

    def is_allowed(self, provider: str) -> bool:
        return provider in self.allowed_providers

    def validate(self, provider: str) -> ProviderPolicyDecision:
        if self.is_allowed(provider):
            return ProviderPolicyDecision(provider=provider, allowed=True)
        return ProviderPolicyDecision(provider=provider, allowed=False, reason="PROVIDER_NOT_SUPPORTED")

    def can_cross_fallback(self) -> bool:
        return self.allow_cross_provider_fallback

    def validate_fallback_target(self, provider: str) -> ProviderPolicyDecision:
        if not self.allow_cross_provider_fallback:
            return ProviderPolicyDecision(provider=provider, allowed=False, reason="FALLBACK_PROVIDER_DISABLED")
        return self.validate(provider)
