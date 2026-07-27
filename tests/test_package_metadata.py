import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


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
