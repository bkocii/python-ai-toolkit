"""Verify an installed core distribution without optional frameworks.

Run this file with the Python executable from a clean virtual environment
containing only the toolkit wheel and its core dependencies.
"""

from __future__ import annotations

import importlib
import importlib.util
import re
import sys
from importlib import metadata
from pathlib import Path

from pydantic import BaseModel

from ai.client import AIClient
from ai.config import AIConfig
from ai.prompts import PromptTemplate
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse
from ai.vector_store import InMemoryVectorStore, VectorRecord

DISTRIBUTION_NAME = "python-ai-toolkit"
EXPECTED_VERSION = "1.0.0"
EXPECTED_CORE_REQUIREMENTS = {
    "openai",
    "pydantic",
    "python-dotenv",
}
OPTIONAL_FRAMEWORKS = {
    "django",
    "fastapi",
}
CORE_MODULES = (
    "ai",
    "ai.agent",
    "ai.async_client",
    "ai.async_executor",
    "ai.cli",
    "ai.cli.config_commands",
    "ai.cli.main",
    "ai.client",
    "ai.config",
    "ai.config_validator",
    "ai.cost",
    "ai.documents",
    "ai.embeddings",
    "ai.exceptions",
    "ai.executor",
    "ai.images",
    "ai.integrations",
    "ai.logger",
    "ai.memory",
    "ai.orchestrator",
    "ai.parser",
    "ai.prompts",
    "ai.providers",
    "ai.providers.base",
    "ai.providers.factory",
    "ai.providers.openai_provider",
    "ai.rag",
    "ai.request_builder",
    "ai.retriever",
    "ai.retry",
    "ai.schemas",
    "ai.structured",
    "ai.tools",
    "ai.vector_store",
    "ai.workflow",
)
OFFLINE_PROVIDER_NAME = "release-core-offline"


class OfflineStructuredResponse(BaseModel):
    answer: str


class OfflineProvider(BaseAIProvider):
    """Deterministic provider for installed client smoke checks."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def ask_text(self, prompt: str) -> ProviderResponse:
        if "The JSON must match this schema:" in prompt:
            return ProviderResponse(text='{"answer": "structured"}')

        return ProviderResponse(text=f"offline:{prompt}")


def canonicalize_distribution_name(name: str) -> str:
    """Return the normalized form used to compare distribution names."""
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(requirement: str) -> str:
    """Extract and normalize a distribution name from Requires-Dist text."""
    name = re.split(r"[\s\[<>=!~;]", requirement, maxsplit=1)[0]
    return canonicalize_distribution_name(name)


def core_requirement_names() -> set[str]:
    """Return requirements that apply without selecting an extra."""
    requirements = metadata.requires(DISTRIBUTION_NAME) or []

    return {
        requirement_name(requirement)
        for requirement in requirements
        if "extra ==" not in requirement
    }


def assert_installed_from_environment() -> Path:
    """Confirm the import resolves from the active virtual environment."""
    ai_module = importlib.import_module("ai")
    if ai_module.__file__ is None:
        raise AssertionError("The installed ai package has no filesystem path.")

    module_path = Path(ai_module.__file__).resolve()
    environment_root = Path(sys.prefix).resolve()

    if not module_path.is_relative_to(environment_root):
        raise AssertionError(
            "The ai package was not imported from the active environment: "
            f"{module_path}"
        )

    return module_path


def assert_optional_frameworks_absent() -> None:
    """Confirm neither optional framework is importable or installed."""
    for framework in sorted(OPTIONAL_FRAMEWORKS):
        if importlib.util.find_spec(framework) is not None:
            raise AssertionError(
                f"Optional framework unexpectedly importable: {framework}"
            )

        try:
            metadata.version(framework)
        except metadata.PackageNotFoundError:
            continue

        raise AssertionError(
            f"Optional framework distribution unexpectedly installed: {framework}"
        )


def import_core_modules() -> None:
    """Import every packaged module outside optional framework adapters."""
    for module_name in CORE_MODULES:
        importlib.import_module(module_name)


def assert_offline_core_behavior() -> None:
    """Exercise representative provider-independent core behavior."""
    rendered = PromptTemplate("Hello {name}").render(name="Burim")
    if rendered != "Hello Burim":
        raise AssertionError("PromptTemplate returned an unexpected result.")

    store = InMemoryVectorStore()
    store.add(
        [
            VectorRecord(
                id="python",
                text="Python toolkit",
                vector=[1.0, 0.0],
            ),
            VectorRecord(
                id="framework",
                text="Optional framework",
                vector=[0.0, 1.0],
            ),
        ]
    )
    results = store.similarity_search([1.0, 0.0], limit=1)

    if len(results) != 1 or results[0].id != "python":
        raise AssertionError("InMemoryVectorStore returned an unexpected result.")


def assert_offline_client_requests() -> None:
    """Exercise installed plain and structured client requests without network."""
    if OFFLINE_PROVIDER_NAME not in ProviderFactory.available_providers():
        ProviderFactory.register(OFFLINE_PROVIDER_NAME, OfflineProvider)

    client = AIClient(
        config=AIConfig(
            provider=OFFLINE_PROVIDER_NAME,
            api_key="release-structure-check",
            model="release-offline-model",
            file_logging_enabled=False,
        )
    )

    if client.ask_text("plain") != "offline:plain":
        raise AssertionError("AIClient returned an unexpected plain response.")

    structured_result = client.ask(
        "Return the structured release answer.",
        response_type=OfflineStructuredResponse,
    )

    if structured_result.data.answer != "structured":
        raise AssertionError("AIClient returned an unexpected structured response.")

    if structured_result.model != "release-offline-model":
        raise AssertionError("AIClient returned unexpected model metadata.")


def verify_core_installation() -> Path:
    """Run the complete installed core-distribution verification."""
    installed_version = metadata.version(DISTRIBUTION_NAME)
    if installed_version != EXPECTED_VERSION:
        raise AssertionError(f"Expected {EXPECTED_VERSION}, found {installed_version}.")

    requirements = core_requirement_names()
    if requirements != EXPECTED_CORE_REQUIREMENTS:
        raise AssertionError(
            "Unexpected core requirements: "
            f"expected {sorted(EXPECTED_CORE_REQUIREMENTS)}, "
            f"found {sorted(requirements)}."
        )

    module_path = assert_installed_from_environment()
    assert_optional_frameworks_absent()
    import_core_modules()
    assert_offline_core_behavior()
    assert_offline_client_requests()

    return module_path


def main() -> int:
    module_path = verify_core_installation()

    print("Core installation verification: PASSED")
    print(f"Version: {EXPECTED_VERSION}")
    print(f"Import path: {module_path}")
    print(f"Core requirements: {', '.join(sorted(EXPECTED_CORE_REQUIREMENTS))}")
    print("Optional frameworks absent: django, fastapi")
    print(f"Core modules imported: {len(CORE_MODULES)}")
    print("Offline prompt and vector-store checks: PASSED")
    print("Offline plain and structured client requests: PASSED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
