from time import perf_counter
from uuid import uuid4
from pydantic import BaseModel
from ai.cost import estimate_cost_usd
from ai.exceptions import AIError, AIJSONParseError, AISchemaValidationError
from ai.logger import get_ai_logger
from ai.parser import parse_json_response
from ai.schemas import AIResult
from typing import Any


class RequestExecutor:
    """
    Executes one AI request from start to finish.

    Responsibilities:
    - Call provider
    - Track duration
    - Retry structured responses once
    - Parse and validate structured responses
    - Calculate cost
    - Log success/failure

    This keeps AIClient small and focused on public API.
    """

    def __init__(self, provider, model: str):
        self.provider = provider
        self.model = model
        self.logger = get_ai_logger()

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
        self.logger.info(
            "AI request succeeded | request_id=%s | model=%s | duration_ms=%.2f | retries_used=%s | tokens=%s | estimated_cost_usd=%s",
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

    def execute(self, prompt: str, response_type: type[BaseModel] | None = None):
        request_id = str(uuid4())
        final_prompt = prompt

        if response_type is not None:
            schema_json = response_type.model_json_schema()
            final_prompt = f"""
{prompt}

Return valid JSON only.
The JSON must match this schema:
{schema_json}
"""

        try:
            start = perf_counter()

            provider_response = self.provider.ask_text(final_prompt)
            raw_response = provider_response.text
            original_raw_response = raw_response
            token_usage = provider_response.token_usage
            retries_used = 0

            if response_type is None:
                duration_ms = (perf_counter() - start) * 1000
                estimated_cost_usd = estimate_cost_usd(self.model, token_usage)

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

            try:
                parsed = parse_json_response(raw_response, response_type)
            except (AIJSONParseError, AISchemaValidationError):
                retries_used = 1

                repair_prompt = f"""
The previous response did not match the required JSON schema.

Original prompt:
{final_prompt}

Invalid response:
{raw_response}

Return ONLY corrected valid JSON matching the schema.
"""
                retry_response = self.provider.ask_text(repair_prompt)
                raw_response = retry_response.text

                token_usage = (
                    token_usage.add(retry_response.token_usage)
                    if token_usage is not None
                    else retry_response.token_usage
                )

                parsed = parse_json_response(raw_response, response_type)

            duration_ms = (perf_counter() - start) * 1000
            estimated_cost_usd = estimate_cost_usd(self.model, token_usage)

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
                "AI request failed | request_id=%s | model=%s",
                request_id,
                self.model,
            )
            raise
