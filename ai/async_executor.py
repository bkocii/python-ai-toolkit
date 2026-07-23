from time import perf_counter
from typing import Any
from uuid import uuid4
import logging
from pydantic import BaseModel

from ai.structured import build_structured_prompt, parse_structured_response
from ai.cost import calculate_cost_usd, resolve_cost_rates
from ai.exceptions import AIError, AIJSONParseError, AISchemaValidationError
from ai.logger import get_ai_logger
from ai.retry import build_json_repair_prompt
from ai.schemas import AIResult


class AsyncRequestExecutor:
    """
    Executes one async AI request from start to finish.

    This mirrors RequestExecutor, but calls async provider methods.
    """

    def __init__(
        self,
        provider,
        model: str,
        max_retries: int = 1,
        logger: logging.Logger | None = None,
        input_cost_per_1m_tokens: str | None = None,
        output_cost_per_1m_tokens: str | None = None,
    ):
        self.provider = provider
        self.model = model
        self.logger = logger if logger is not None else get_ai_logger()
        self.max_retries = max_retries
        self._cost_rates = resolve_cost_rates(
            model=model,
            input_cost_per_1m_tokens=(input_cost_per_1m_tokens),
            output_cost_per_1m_tokens=(output_cost_per_1m_tokens),
        )

    def _log_success(
        self,
        request_id: str,
        duration_ms: float,
        retries_used: int,
        token_usage,
        estimated_cost_usd,
    ) -> None:
        """
        Log successful AI request metadata.

        Prompt and response content are intentionally not logged.
        """

        if not self.logger.isEnabledFor(logging.INFO):
            return

        self.logger.info(
            "Async AI request succeeded | request_id=%s | model=%s | duration_ms=%.2f | retries_used=%s | tokens=%s | estimated_cost_usd=%s",
            request_id,
            self.model,
            duration_ms,
            retries_used,
            token_usage.model_dump() if token_usage else None,
            estimated_cost_usd,
        )

    def _build_result(
        self,
        data: Any,
        raw_response: str,
        request_id: str,
        original_raw_response: str,
        duration_ms: float,
        retries_used: int,
        token_usage,
        estimated_cost_usd,
    ) -> AIResult:
        """
        Build the standard AIResult object returned by the toolkit.
        """
        return AIResult(
            data=data,
            model=self.model,
            raw_response=raw_response,
            request_id=request_id,
            original_raw_response=original_raw_response,
            duration_ms=duration_ms,
            retries_used=retries_used,
            token_usage=token_usage,
            estimated_cost_usd=estimated_cost_usd,
        )

    async def execute(
        self,
        prompt: str,
        response_type: type[BaseModel] | None = None,
    ):
        request_id = str(uuid4())
        final_prompt = prompt

        if response_type is not None:
            final_prompt = build_structured_prompt(
                prompt=prompt,
                response_type=response_type,
            )

        try:
            start = perf_counter()

            provider_response = await self.provider.ask_text_async(final_prompt)
            raw_response = provider_response.text
            original_raw_response = raw_response
            token_usage = provider_response.token_usage
            retries_used = 0

            if response_type is None:
                duration_ms = (perf_counter() - start) * 1000
                estimated_cost_usd = calculate_cost_usd(
                    token_usage=token_usage,
                    prices=self._cost_rates,
                )

                self._log_success(
                    request_id=request_id,
                    duration_ms=duration_ms,
                    retries_used=retries_used,
                    token_usage=token_usage,
                    estimated_cost_usd=estimated_cost_usd,
                )

                return self._build_result(
                    data=raw_response,
                    raw_response=raw_response,
                    request_id=request_id,
                    original_raw_response=original_raw_response,
                    duration_ms=duration_ms,
                    retries_used=retries_used,
                    token_usage=token_usage,
                    estimated_cost_usd=estimated_cost_usd,
                )

            while True:
                try:
                    parsed = parse_structured_response(raw_response, response_type)
                    break
                except (AIJSONParseError, AISchemaValidationError):
                    if retries_used >= self.max_retries:
                        raise

                    retries_used += 1

                    repair_prompt = build_json_repair_prompt(
                        original_prompt=final_prompt,
                        invalid_response=raw_response,
                    )

                    retry_response = await self.provider.ask_text_async(repair_prompt)
                    raw_response = retry_response.text

                    token_usage = (
                        token_usage.add(retry_response.token_usage)
                        if token_usage is not None
                        else retry_response.token_usage
                    )

            duration_ms = (perf_counter() - start) * 1000
            estimated_cost_usd = calculate_cost_usd(
                token_usage=token_usage,
                prices=self._cost_rates,
            )

            self._log_success(
                request_id=request_id,
                duration_ms=duration_ms,
                retries_used=retries_used,
                token_usage=token_usage,
                estimated_cost_usd=estimated_cost_usd,
            )

            return self._build_result(
                data=parsed,
                raw_response=raw_response,
                request_id=request_id,
                original_raw_response=original_raw_response,
                duration_ms=duration_ms,
                retries_used=retries_used,
                token_usage=token_usage,
                estimated_cost_usd=estimated_cost_usd,
            )

        except AIError:
            self.logger.exception(
                "Async AI request failed | request_id=%s | model=%s",
                request_id,
                self.model,
            )
            raise
