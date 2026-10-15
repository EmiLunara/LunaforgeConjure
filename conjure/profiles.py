from dataclasses import dataclass
from pathlib import Path
import tomllib

from conjure.generators.cpp import CppOptions

@dataclass(frozen=True)
class CppProfile:
    """Reusable configuration for C++ file generation."""

    namespace: str = ""

    output: Path = Path(".")
    split: bool = False

    header_root: Path | None = None
    source_root: Path | None = None

    include_prefix: Path | None = None

def load_cpp_profile(config_path: Path, profile_name: str) -> CppProfile:
    """Load a named C++ profile from a TOML configuration file."""

    with config_path.open("rb") as file:
        config = tomllib.load(file)

    profiles = config.get("profiles", {})

    if not isinstance(profiles, dict):
        raise ValueError("'profiles' must be a TOML table.")

    profile = profiles.get(profile_name)

    if profile is None:
        raise ValueError(f"Unknown profile: {profile_name}")

    if not isinstance(profile, dict):
        raise ValueError(f"Profile '{profile_name}' must be a table.")

    allowed_fields = {
        "namespace",
        "output",
        "split",
        "header_root",
        "source_root",
        "include_prefix",
    }

    unknown_fields = set(profile) - allowed_fields

    if unknown_fields:
        raise ValueError(f"Unknown profile settings: {', '.join(sorted(unknown_fields))}")

    for field in ("namespace", "output", "header_root", "source_root", "include_prefix"):
        if field in profile and not isinstance(profile[field], str):
            raise ValueError(f"'{field}' must be a string.")

    if "split" in profile and not isinstance(profile["split"], bool):
        raise ValueError("'split' must be a boolean.")

    has_header_root = "header_root" in profile
    has_source_root = "source_root" in profile

    if has_header_root != has_source_root:
        raise ValueError("'header_root' and 'source_root' must be specified together.")

    if profile.get("split", False) and has_header_root:
        raise ValueError("'split' cannot be combined with custom header/source roots.")

    project_root = config_path.resolve().parent

    def resolve_directory(value: str | None) -> Path | None:
        if value is None:
            return None

        path = Path(value)
        return path if path.is_absolute() else project_root / path

    return CppProfile(
        namespace=profile.get("namespace", ""),
        output=resolve_directory(profile.get("output", ".")),
        split=profile.get("split", False),
        header_root=resolve_directory(profile.get("header_root")),
        source_root=resolve_directory(profile.get("source_root")),
        include_prefix=(Path(profile["include_prefix"]) if "include_prefix" in profile else None),
    )

def create_cpp_options(profile: CppProfile, name: str, subdir: Path = Path("."),namespace_append: str = "") -> CppOptions:
    """Combine a reusable C++ profile with generation arguments."""

    return CppOptions(
        name=name,
        namespace=compose_namespace(profile.namespace, namespace_append),
        output=profile.output,
        split=profile.split,
        header_root=profile.header_root,
        source_root=profile.source_root,
        subdir=subdir,
        include_prefix=profile.include_prefix,
    )

def find_project_config(start_directory: Path | None = None) -> Path | None:
    """Find .conjure.toml in the current directory or its parents."""

    if start_directory is None:
        start_directory = Path.cwd()

    current = start_directory.resolve()

    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        config_path = directory / ".conjure.toml"

        if config_path.is_file():
            return config_path

    return None

def compose_namespace(base: str, extension: str) -> str:
    """Append a namespace to a base namespace."""

    if not base:
        return extension

    if not extension:
        return base

    return f"{base}::{extension}"