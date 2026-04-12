"""Thin Gemini client for text generation. Business prompts live in ai_guidance_service."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from typing import Any

from app.core.config import get_settings

_logger = logging.getLogger(__name__)

# TODO: structured retries, request IDs, redaction in logs, and usage metrics.

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="gemini")


class GeminiUnavailableError(Exception):
    """Raised when API key is missing or SDK cannot run."""


class GeminiGenerationError(Exception):
    """Raised when the model returns no usable text."""


def _import_genai() -> Any:
    try:
        import google.generativeai as genai  # type: ignore[import-not-found]

        return genai
    except ImportError as exc:  # pragma: no cover
        raise GeminiUnavailableError("google-generativeai is not installed.") from exc


class GeminiTextClient:
    """Low-level wrapper: configure once per process, generate with timeout."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = (settings.GEMINI_API_KEY or "").strip()
        self._model_name = (settings.GEMINI_MODEL or "gemini-2.0-flash").strip()

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate_text(
        self,
        *,
        prompt: str,
        timeout_seconds: float = 28.0,
        max_output_tokens: int = 512,
        temperature: float = 0.35,
    ) -> str:
        if not self.is_configured:
            raise GeminiUnavailableError("GEMINI_API_KEY is not set.")

        genai = _import_genai()
        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(self._model_name)

        def _call() -> str:
            resp = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                ),
            )
            text = (getattr(resp, "text", None) or "").strip()
            if not text and getattr(resp, "candidates", None):
                # Some responses only expose candidates/parts.
                parts: list[str] = []
                for c in resp.candidates or []:
                    content = getattr(c, "content", None)
                    if content is None:
                        continue
                    for p in getattr(content, "parts", []) or []:
                        t = getattr(p, "text", None)
                        if t:
                            parts.append(str(t))
                text = "\n".join(parts).strip()
            if not text:
                raise GeminiGenerationError("Empty model response.")
            return text

        fut = _EXECUTOR.submit(_call)
        try:
            return fut.result(timeout=timeout_seconds)
        except FuturesTimeout as exc:
            fut.cancel()
            raise GeminiGenerationError("Gemini request timed out.") from exc
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Gemini generate_text failed: %s", exc)
            raise GeminiGenerationError(str(exc)) from exc


_client: GeminiTextClient | None = None


def get_gemini_text_client() -> GeminiTextClient:
    global _client
    if _client is None:
        _client = GeminiTextClient()
    return _client
