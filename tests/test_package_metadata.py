import ast
import importlib.metadata
import tomllib
from pathlib import Path

from ai.cli.main import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
EXPECTED_CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Framework :: Django",
    "Framework :: FastAPI",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
EXPECTED_OPTIONAL_DEPENDENCIES = {
    "django": [
        "django>=5.0",
    ],
    "fastapi": [
        "fastapi>=0.100,<1",
    ],
    "dev": [
        "pytest",
        "black",
        "ruff",
        "django>=5.0",
        "fastapi>=0.100,<1",
        "httpx2",
    ],
    "benchmark": [
        "pytest",
        "pytest-benchmark",
    ],
}


def load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def test_core_package_metadata_matches_project_identity():
    project = load_pyproject()["project"]

    assert project["name"] == "python-ai-toolkit"
    assert project["version"] == "0.7.0.dev0"
    assert project["description"] == (
        "Reusable infrastructure for integrating LLMs into Python applications."
    )
    assert project["requires-python"] == ">=3.11"
    assert project["authors"] == [{"name": "Burim Koci"}]


def test_readme_metadata_uses_the_project_readme():
    project = load_pyproject()["project"]
    readme_path = PROJECT_ROOT / project["readme"]
    readme = readme_path.read_text(encoding="utf-8")

    assert project["readme"] == "README.md"
    assert readme.startswith("# Python AI Toolkit\n")
    assert "`0.7.0-dev`" in readme


def test_core_dependencies_express_runtime_compatibility_boundaries():
    project = load_pyproject()["project"]

    assert project["dependencies"] == [
        "openai>=1.66.0",
        "pydantic>=2.4.2",
        "python-dotenv",
    ]


def test_optional_dependency_groups_match_supported_workflows():
    optional_dependencies = load_pyproject()["project"]["optional-dependencies"]

    assert optional_dependencies == EXPECTED_OPTIONAL_DEPENDENCIES
    assert set(optional_dependencies["django"]).issubset(optional_dependencies["dev"])
    assert set(optional_dependencies["fastapi"]).issubset(optional_dependencies["dev"])
    assert "httpx2" in optional_dependencies["dev"]
    assert "httpx2" not in optional_dependencies["fastapi"]
    assert optional_dependencies["benchmark"] == ["pytest", "pytest-benchmark"]


def test_core_dependencies_exclude_optional_workflow_packages():
    core_dependencies = load_pyproject()["project"]["dependencies"]
    optional_package_names = {
        "black",
        "django",
        "fastapi",
        "httpx2",
        "pytest",
        "pytest-benchmark",
        "ruff",
    }

    assert not any(
        dependency.split("<", 1)[0].split(">", 1)[0].split("=", 1)[0]
        in optional_package_names
        for dependency in core_dependencies
    )


def test_optional_framework_imports_stay_within_integration_packages():
    framework_directories = {
        "django": PROJECT_ROOT / "ai" / "integrations" / "django",
        "fastapi": PROJECT_ROOT / "ai" / "integrations" / "fastapi",
    }

    for source_path in (PROJECT_ROOT / "ai").rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=source_path)
        imported_roots = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_roots.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        for framework, integration_directory in framework_directories.items():
            if framework in imported_roots:
                assert source_path.is_relative_to(integration_directory)


def test_package_classifiers_describe_the_current_project():
    project = load_pyproject()["project"]

    assert project["classifiers"] == EXPECTED_CLASSIFIERS


def test_package_classifiers_do_not_overstate_unverified_or_unowned_metadata():
    classifiers = load_pyproject()["project"]["classifiers"]

    assert not any(classifier.startswith("License ::") for classifier in classifiers)
    assert not any(
        classifier.startswith("Programming Language :: Python :: 3.")
        for classifier in classifiers
    )
    assert "Development Status :: 5 - Production/Stable" not in classifiers


def test_mit_license_metadata_matches_the_repository_license():
    project = load_pyproject()["project"]
    license_paths = [
        PROJECT_ROOT / relative_path for relative_path in project["license-files"]
    ]

    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert license_paths == [PROJECT_ROOT / "LICENSE"]

    license_text = license_paths[0].read_text(encoding="utf-8")

    assert license_text.startswith("MIT License\n\nCopyright (c) 2026 Burim Koci\n")
    assert "Permission is hereby granted, free of charge" in license_text
    assert "The above copyright notice and this permission notice" in license_text
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in license_text


def test_build_backend_supports_current_license_metadata():
    build_requirements = load_pyproject()["build-system"]["requires"]

    assert build_requirements == ["setuptools>=77.0.3", "wheel"]


def test_generated_package_build_outputs_are_ignored():
    ignored_paths = {
        line.strip()
        for line in GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert {"build/", "dist/", "*.egg-info/"}.issubset(ignored_paths)


def test_console_script_metadata_targets_supported_cli_main():
    scripts = load_pyproject()["project"]["scripts"]

    assert scripts == {
        "ai-toolkit": "ai.cli.main:main",
    }


def test_installed_console_entry_point_loads_supported_cli_main():
    distribution_name = load_pyproject()["project"]["name"]
    console_scripts = [
        entry_point
        for entry_point in importlib.metadata.distribution(
            distribution_name
        ).entry_points
        if entry_point.group == "console_scripts"
    ]

    assert [
        (entry_point.name, entry_point.value) for entry_point in console_scripts
    ] == [
        ("ai-toolkit", "ai.cli.main:main"),
    ]
    assert console_scripts[0].load() is main


def test_package_discovery_covers_every_ai_package():
    pyproject = load_pyproject()
    discovery = pyproject["tool"]["setuptools"]["packages"]["find"]
    package_directories = {
        path.parent.relative_to(PROJECT_ROOT).as_posix().replace("/", ".")
        for path in (PROJECT_ROOT / "ai").rglob("__init__.py")
    }

    assert discovery == {
        "where": ["."],
        "include": ["ai*"],
    }
    assert package_directories == {
        "ai",
        "ai.cli",
        "ai.integrations",
        "ai.integrations.django",
        "ai.integrations.fastapi",
        "ai.providers",
    }
