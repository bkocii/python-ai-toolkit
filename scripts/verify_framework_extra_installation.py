"""Verify one installed framework extra without the other framework.

Run this file with the Python executable from a clean virtual environment
containing the toolkit wheel with either the ``django`` or ``fastapi`` extra.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import re
import sys
from importlib import metadata
from pathlib import Path
from typing import Annotated, get_args, get_origin

from ai.client import AIClient
from ai.providers.base import BaseAIProvider
from ai.providers.factory import ProviderFactory
from ai.schemas import ProviderResponse

DISTRIBUTION_NAME = "python-ai-toolkit"
EXPECTED_VERSION = "1.0.0"
EXPECTED_EXTRA_REQUIREMENTS = {
    "django": "django>=5.0",
    "fastapi": "fastapi>=0.100,<1",
}
FRAMEWORK_ADAPTER_MODULES = {
    "django": (
        "ai.integrations.django",
        "ai.integrations.django.client",
        "ai.integrations.django.config",
    ),
    "fastapi": (
        "ai.integrations.fastapi",
        "ai.integrations.fastapi.dependencies",
    ),
}
OFFLINE_PROVIDER_NAME = "package010-offline"


class OfflineProvider(BaseAIProvider):
    """Small provider used to exercise an adapter without network access."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text=f"offline:{prompt}")


def requirement_name(requirement: str) -> str:
    """Extract the normalized distribution name from Requires-Dist text."""
    name = re.split(r"[\s\[<>=!~;]", requirement, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name).lower()


def extra_requirement_names(extra: str) -> set[str]:
    """Return installed requirements guarded by the selected extra marker."""
    requirements = metadata.requires(DISTRIBUTION_NAME) or []
    marker_pattern = re.compile(
        rf"""extra\s*==\s*["']{re.escape(extra)}["']""",
        flags=re.IGNORECASE,
    )

    return {
        requirement_name(requirement)
        for requirement in requirements
        if marker_pattern.search(requirement)
    }


def assert_module_from_environment(module_name: str) -> Path:
    """Import a module and confirm it resolves from the active environment."""
    module = importlib.import_module(module_name)
    module_file = getattr(module, "__file__", None)

    if module_file is None:
        raise AssertionError(f"Installed module has no filesystem path: {module_name}")

    module_path = Path(module_file).resolve()
    environment_root = Path(sys.prefix).resolve()

    if not module_path.is_relative_to(environment_root):
        raise AssertionError(
            f"{module_name} was not imported from the active environment: "
            f"{module_path}"
        )

    return module_path


def assert_framework_absent(framework: str) -> None:
    """Confirm an unselected framework is neither importable nor installed."""
    if importlib.util.find_spec(framework) is not None:
        raise AssertionError(f"Unselected framework is importable: {framework}")

    try:
        metadata.version(framework)
    except metadata.PackageNotFoundError:
        return

    raise AssertionError(f"Unselected framework is installed: {framework}")


def register_offline_provider() -> None:
    """Register the deterministic provider used by both adapter smoke checks."""
    if OFFLINE_PROVIDER_NAME not in ProviderFactory.available_providers():
        ProviderFactory.register(OFFLINE_PROVIDER_NAME, OfflineProvider)


def configure_offline_environment() -> None:
    """Configure environment-based clients without real credentials or logging."""
    os.environ["AI_PROVIDER"] = OFFLINE_PROVIDER_NAME
    os.environ["AI_API_KEY"] = "package-010-structure-check"
    os.environ["AI_MODEL"] = "package-010-model"
    os.environ["AI_FILE_LOGGING_ENABLED"] = "false"


def verify_django_adapter() -> str:
    """Exercise Django settings translation and client construction offline."""
    import django
    from django.conf import settings

    if django.VERSION < (5, 0):
        raise AssertionError(
            f"Django 5.0 or newer required, found {django.get_version()}."
        )

    if not settings.configured:
        settings.configure(
            SECRET_KEY="package-010",
            AI_TOOLKIT={
                "provider": OFFLINE_PROVIDER_NAME,
                "api_key": "package-010-structure-check",
                "model": "package-010-model",
                "file_logging_enabled": False,
            },
        )

    django.setup()

    from ai.integrations.django import get_ai_client, get_django_ai_config

    config = get_django_ai_config()
    if config.provider != OFFLINE_PROVIDER_NAME:
        raise AssertionError("Django adapter returned the wrong provider.")
    if config.model != "package-010-model":
        raise AssertionError("Django adapter returned the wrong model.")
    if config.file_logging_enabled:
        raise AssertionError("Django adapter did not disable file logging.")

    client = get_ai_client()
    if not isinstance(client, AIClient):
        raise TypeError("Django adapter did not construct AIClient.")
    if client.ask_text("django") != "offline:django":
        raise AssertionError("Django adapter returned an unexpected offline response.")

    return django.get_version()


def parse_version_prefix(version: str) -> tuple[int, ...]:
    """Return the leading numeric release tuple from a version string."""
    match = re.match(r"\d+(?:\.\d+)*", version)
    if match is None:
        raise AssertionError(f"Cannot parse framework version: {version}")

    return tuple(int(part) for part in match.group(0).split("."))


def verify_fastapi_adapter() -> str:
    """Exercise dependency aliases and client construction offline."""
    import fastapi
    from fastapi import Depends, FastAPI
    from fastapi.params import Depends as DependsParameter

    fastapi_version = parse_version_prefix(fastapi.__version__)
    if fastapi_version < (0, 100) or fastapi_version >= (1,):
        raise AssertionError(
            "FastAPI version must satisfy >=0.100,<1; " f"found {fastapi.__version__}."
        )

    from ai.integrations.fastapi import (
        AIClientDependency,
        AsyncAIClientDependency,
        get_ai_client,
        get_async_ai_client,
    )

    for alias, client_type, dependency_function in (
        (AIClientDependency, AIClient, get_ai_client),
        (
            AsyncAIClientDependency,
            importlib.import_module("ai.async_client").AsyncAIClient,
            get_async_ai_client,
        ),
    ):
        arguments = get_args(alias)
        if get_origin(alias) is not Annotated or arguments[0] is not client_type:
            raise AssertionError("FastAPI adapter exposes an invalid dependency alias.")
        if not isinstance(arguments[1], DependsParameter):
            raise TypeError("FastAPI alias does not contain Depends metadata.")
        if arguments[1].dependency is not dependency_function:
            raise AssertionError("FastAPI alias targets the wrong dependency function.")

    app = FastAPI()
    client_dependency = Depends(get_ai_client)

    @app.get("/offline")
    def offline(client=client_dependency):
        return {"result": client.ask_text("fastapi")}

    client = get_ai_client()
    if not isinstance(client, AIClient):
        raise TypeError("FastAPI adapter did not construct AIClient.")
    if client.ask_text("fastapi") != "offline:fastapi":
        raise AssertionError("FastAPI adapter returned an unexpected offline response.")
    if not any(getattr(route, "path", None) == "/offline" for route in app.routes):
        raise AssertionError("FastAPI did not register the adapter-backed route.")

    return fastapi.__version__


def verify_framework_extra(extra: str) -> tuple[Path, str, str]:
    """Run the complete installed-extra verification for one framework."""
    if extra not in EXPECTED_EXTRA_REQUIREMENTS:
        choices = ", ".join(sorted(EXPECTED_EXTRA_REQUIREMENTS))
        raise ValueError(f"Unsupported framework extra '{extra}'. Choose: {choices}.")

    installed_version = metadata.version(DISTRIBUTION_NAME)
    if installed_version != EXPECTED_VERSION:
        raise AssertionError(f"Expected {EXPECTED_VERSION}, found {installed_version}.")

    declared_extras = set(
        metadata.distribution(DISTRIBUTION_NAME).metadata.get_all(
            "Provides-Extra",
            [],
        )
    )
    if extra not in declared_extras:
        raise AssertionError(f"Installed distribution does not declare extra: {extra}")

    requirement_names = extra_requirement_names(extra)
    if requirement_names != {extra}:
        raise AssertionError(
            f"Unexpected requirements for extra '{extra}': "
            f"expected {[extra]}, found {sorted(requirement_names)}."
        )

    other_framework = (set(EXPECTED_EXTRA_REQUIREMENTS) - {extra}).pop()
    assert_framework_absent(other_framework)

    toolkit_path = assert_module_from_environment("ai")
    assert_module_from_environment(extra)
    for module_name in FRAMEWORK_ADAPTER_MODULES[extra]:
        assert_module_from_environment(module_name)

    register_offline_provider()
    configure_offline_environment()

    if extra == "django":
        framework_version = verify_django_adapter()
    else:
        framework_version = verify_fastapi_adapter()

    return toolkit_path, framework_version, other_framework


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify one installed Python AI Toolkit framework extra.",
    )
    parser.add_argument(
        "extra",
        choices=sorted(EXPECTED_EXTRA_REQUIREMENTS),
        help="Framework extra installed in the active clean environment.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    toolkit_path, framework_version, absent_framework = verify_framework_extra(
        args.extra
    )

    framework_label = {
        "django": "Django",
        "fastapi": "FastAPI",
    }[args.extra]

    print(f"{framework_label} extra verification: PASSED")
    print(f"Toolkit version: {EXPECTED_VERSION}")
    print(f"Toolkit import path: {toolkit_path}")
    print(f"Framework version: {framework_version}")
    print(f"Unselected framework absent: {absent_framework}")
    print("Installed adapter modules: PASSED")
    print("Offline integration behavior: PASSED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
