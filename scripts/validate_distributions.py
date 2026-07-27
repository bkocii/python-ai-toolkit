"""Validate built Python AI Toolkit distributions without installing them."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import tarfile
import tomllib
import zipfile
from email.message import Message
from email.parser import BytesParser
from email.policy import default
from pathlib import Path, PurePosixPath

FORBIDDEN_PARTS = {
    ".benchmarks",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "deliverables",
    "dist",
    "logs",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
EXPECTED_SDIST_ROOT_ENTRIES = {
    "LICENSE",
    "PKG-INFO",
    "README.md",
    "ai",
    "pyproject.toml",
    "python_ai_toolkit.egg-info",
    "setup.cfg",
    "tests",
}


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_sha256(path: Path) -> str:
    return sha256_hex(path.read_bytes())


def assert_safe_archive_path(name: str) -> PurePosixPath:
    assert "\\" not in name, f"archive path uses a backslash: {name}"
    path = PurePosixPath(name)
    assert not path.is_absolute(), f"archive path is absolute: {name}"
    assert ".." not in path.parts, f"archive path traverses upward: {name}"
    assert all(
        part not in {"", "."} for part in path.parts
    ), f"archive path is not normalized: {name}"
    return path


def assert_no_unintended_content(paths: set[PurePosixPath]) -> None:
    for path in paths:
        assert not FORBIDDEN_PARTS.intersection(
            path.parts
        ), f"generated or unintended path is packaged: {path}"
        assert (
            path.suffix not in FORBIDDEN_SUFFIXES
        ), f"compiled Python file is packaged: {path}"
        assert not any(
            part == ".env" or part.startswith(".env.") for part in path.parts
        ), f"environment file is packaged: {path}"


def parse_metadata(data: bytes) -> Message:
    return BytesParser(policy=default).parsebytes(data)


def metadata_description(data: bytes) -> str:
    separator = b"\r\n\r\n" if b"\r\n\r\n" in data else b"\n\n"
    headers, found, description = data.partition(separator)
    assert found and headers
    return description.decode("utf-8")


def normalize_text_newlines(text: str) -> str:
    """Return text with platform-specific line endings normalized to LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def assert_metadata_matches(
    metadata: Message,
    *,
    description: str,
    project: dict,
    readme: str,
) -> None:
    expected_author = ", ".join(author["name"] for author in project["authors"])

    assert metadata["Name"] == project["name"]
    assert metadata["Version"] == project["version"]
    assert metadata["Summary"] == project["description"]
    assert metadata["Author"] == expected_author
    assert metadata["Requires-Python"] == project["requires-python"]
    assert metadata["License-Expression"] == project["license"]
    assert metadata.get_all("License-File") == project["license-files"]
    assert metadata["Description-Content-Type"] == "text/markdown"
    assert normalize_text_newlines(description) == normalize_text_newlines(
        readme
    ), "packaged long description differs from README.md"

    requirements = metadata.get_all("Requires-Dist")
    for dependency in project["dependencies"]:
        assert dependency in requirements
    assert metadata.get_all("Provides-Extra") == list(project["optional-dependencies"])


def source_python_files(source_root: Path, relative_root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in sorted((source_root / relative_root).rglob("*.py"))
    }


def assert_wheel_record(
    archive: zipfile.ZipFile,
    *,
    record_name: str,
) -> None:
    rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
    records = {name: (digest, size) for name, digest, size in rows}

    assert set(records) == set(archive.namelist())
    for name in archive.namelist():
        digest, size = records[name]
        if name == record_name:
            assert digest == ""
            assert size == ""
            continue

        data = archive.read(name)
        algorithm, encoded_digest = digest.split("=", 1)
        assert algorithm == "sha256"
        actual_digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(
            b"="
        )
        assert encoded_digest == actual_digest.decode("ascii")
        assert int(size) == len(data)


def validate_wheel(
    wheel_path: Path,
    *,
    source_root: Path,
    project: dict,
    readme: str,
    license_text: bytes,
) -> tuple[int, Message]:
    distribution = project["name"].replace("-", "_")
    version = project["version"]
    expected_filename = f"{distribution}-{version}-py3-none-any.whl"
    assert wheel_path.name == expected_filename

    dist_info = f"{distribution}-{version}.dist-info"
    with zipfile.ZipFile(wheel_path) as archive:
        names = archive.namelist()
        paths = {assert_safe_archive_path(name) for name in names}
        assert_no_unintended_content(paths)
        assert {path.parts[0] for path in paths} == {"ai", dist_info}

        archived_python = {
            name: archive.read(name)
            for name in names
            if name.startswith("ai/") and name.endswith(".py")
        }
        assert archived_python == source_python_files(source_root, Path("ai"))

        metadata_name = f"{dist_info}/METADATA"
        wheel_metadata_name = f"{dist_info}/WHEEL"
        entry_points_name = f"{dist_info}/entry_points.txt"
        license_name = f"{dist_info}/licenses/LICENSE"
        record_name = f"{dist_info}/RECORD"
        required = {
            metadata_name,
            wheel_metadata_name,
            entry_points_name,
            license_name,
            record_name,
        }
        assert required.issubset(names)

        metadata_bytes = archive.read(metadata_name)
        metadata = parse_metadata(metadata_bytes)
        assert_metadata_matches(
            metadata,
            description=metadata_description(metadata_bytes),
            project=project,
            readme=readme,
        )
        assert archive.read(license_name) == license_text
        assert archive.read(entry_points_name).decode("utf-8") == (
            "[console_scripts]\n" f"ai-toolkit = {project['scripts']['ai-toolkit']}\n"
        )

        wheel_metadata = parse_metadata(archive.read(wheel_metadata_name))
        assert wheel_metadata["Root-Is-Purelib"] == "true"
        assert wheel_metadata.get_all("Tag") == ["py3-none-any"]
        assert_wheel_record(archive, record_name=record_name)

    return len(names), metadata


def validate_sdist(
    sdist_path: Path,
    *,
    source_root: Path,
    project: dict,
    readme: str,
    license_text: bytes,
) -> tuple[int, Message]:
    distribution = project["name"].replace("-", "_")
    version = project["version"]
    archive_root = f"{distribution}-{version}"
    assert sdist_path.name == f"{archive_root}.tar.gz"

    with tarfile.open(sdist_path, mode="r:gz") as archive:
        members = archive.getmembers()
        paths = {assert_safe_archive_path(member.name) for member in members}
        assert_no_unintended_content(paths)
        assert all(
            member.isfile() or member.isdir() for member in members
        ), "source distribution contains a link or special filesystem entry"
        assert {path.parts[0] for path in paths} == {archive_root}

        root_entries = {path.parts[1] for path in paths if len(path.parts) >= 2}
        assert root_entries == EXPECTED_SDIST_ROOT_ENTRIES

        files = {
            member.name: archive.extractfile(member).read()
            for member in members
            if member.isfile()
        }
        archived_python = {
            name.removeprefix(f"{archive_root}/"): data
            for name, data in files.items()
            if name.startswith(f"{archive_root}/ai/") and name.endswith(".py")
        }
        assert archived_python == source_python_files(source_root, Path("ai"))

        archived_tests = {
            name.removeprefix(f"{archive_root}/"): data
            for name, data in files.items()
            if name.startswith(f"{archive_root}/tests/") and name.endswith(".py")
        }
        assert archived_tests == source_python_files(source_root, Path("tests"))

        assert normalize_text_newlines(
            files[f"{archive_root}/README.md"].decode("utf-8")
        ) == normalize_text_newlines(
            readme
        ), "source-distribution README.md differs from the project README.md"
        assert files[f"{archive_root}/LICENSE"] == license_text
        assert (
            files[f"{archive_root}/pyproject.toml"]
            == (source_root / "pyproject.toml").read_bytes()
        )

        metadata_bytes = files[f"{archive_root}/PKG-INFO"]
        metadata = parse_metadata(metadata_bytes)
        assert_metadata_matches(
            metadata,
            description=metadata_description(metadata_bytes),
            project=project,
            readme=readme,
        )

    return len(members), metadata


def validate_distributions(source_root: Path, dist_directory: Path) -> None:
    pyproject = tomllib.loads(
        (source_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = pyproject["project"]
    readme = (source_root / project["readme"]).read_text(encoding="utf-8")
    license_text = (source_root / project["license-files"][0]).read_bytes()

    wheels = sorted(dist_directory.glob("*.whl"))
    sdists = sorted(dist_directory.glob("*.tar.gz"))
    assert len(wheels) == 1, f"expected one wheel, found {len(wheels)}"
    assert len(sdists) == 1, f"expected one source distribution, found {len(sdists)}"

    wheel_count, wheel_metadata = validate_wheel(
        wheels[0],
        source_root=source_root,
        project=project,
        readme=readme,
        license_text=license_text,
    )
    sdist_count, sdist_metadata = validate_sdist(
        sdists[0],
        source_root=source_root,
        project=project,
        readme=readme,
        license_text=license_text,
    )
    assert wheel_metadata.items() == sdist_metadata.items()

    print(f"Validated wheel: {wheels[0].name} ({wheel_count} entries)")
    print(f"SHA-256: {archive_sha256(wheels[0])}")
    print(f"Validated source distribution: {sdists[0].name} ({sdist_count} entries)")
    print(f"SHA-256: {archive_sha256(sdists[0])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="project source root (default: parent of this script directory)",
    )
    parser.add_argument(
        "--dist-directory",
        type=Path,
        default=None,
        help="distribution directory (default: SOURCE_ROOT/dist)",
    )
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    dist_directory = (
        args.dist_directory.resolve() if args.dist_directory else source_root / "dist"
    )
    validate_distributions(source_root, dist_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
