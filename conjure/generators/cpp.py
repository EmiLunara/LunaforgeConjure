from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from conjure.models import GeneratedFile

import keyword
import re


@dataclass(frozen=True)
class CppPaths:
    """Resolved locations for a C++ header/source pair."""

    header: Path
    source: Path
    include: str

@dataclass(frozen=True)
class CppOptions:
    """Configuration for generating C++ files."""

    name: str
    namespace: str = ""
    output: Path = Path(".")
    split: bool = False

    header_root: Path | None = None
    source_root: Path | None = None

    subdir: Path = Path(".")
    include_prefix: Path | None = None


CPP_KEYWORDS = {
    "alignas", "alignof", "asm", "auto", "bool", "break",
    "case", "catch", "char", "char8_t", "char16_t", "char32_t",
    "class", "const", "consteval", "constexpr", "constinit",
    "const_cast", "continue", "co_await", "co_return",
    "co_yield", "decltype", "default", "delete", "do",
    "double", "dynamic_cast", "else", "enum", "explicit",
    "export", "extern", "false", "float", "for", "friend",
    "goto", "if", "inline", "int", "long", "mutable",
    "namespace", "new", "noexcept", "nullptr", "operator",
    "private", "protected", "public", "register",
    "reinterpret_cast", "requires", "return", "short",
    "signed", "sizeof", "static", "static_assert",
    "static_cast", "struct", "switch", "template", "this",
    "thread_local", "throw", "true", "try", "typedef",
    "typeid", "typename", "union", "unsigned", "using",
    "virtual", "void", "volatile", "wchar_t", "while",
    "and", "and_eq", "bitand", "bitor", "compl",
    "not", "not_eq", "or", "or_eq", "xor", "xor_eq",
    "final", "override", "import", "module",
}


def is_valid_cpp_identifier(name: str) -> bool:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return False

    if name in CPP_KEYWORDS:
        return False

    # Reject reserved implementation identifiers.
    if "__" in name or name.startswith("_"):
        return False

    return True


def validate_cpp_options(options: CppOptions) -> None:
    """Validate C++ names before generating files."""

    if not is_valid_cpp_identifier(options.name):
        raise ValueError(f"Invalid C++ class name: {options.name}")

    if options.namespace:
        parts = options.namespace.split("::")

        if not all(is_valid_cpp_identifier(part) for part in parts):
            raise ValueError(f"Invalid C++ namespace: {options.namespace}")

def validate_relative_path(path: Path, name: str) -> None:
    """Validate a relative subdirectory or include prefix."""

    windows_path = PureWindowsPath(str(path))

    if path.is_absolute() or windows_path.drive or windows_path.root:
        raise ValueError(f"{name} must be a relative path: {path}")

    if ".." in path.parts or ".." in windows_path.parts:
        raise ValueError(f"{name} cannot contain parent traversal: {path}")

def resolve_paths(options: CppOptions) -> CppPaths:
    """Resolve C++ header, source and include paths."""

    custom_roots = (options.header_root is not None or options.source_root is not None)

    if custom_roots:
        if options.header_root is None or options.source_root is None:
            raise ValueError("Both header_root and source_root are required.")

        if options.split:
            raise ValueError("Split layout cannot be combined with custom roots.")

        header_root = options.header_root
        source_root = options.source_root

    elif options.split:
        header_root = options.output / "Public"
        source_root = options.output / "Private"

    else:
        header_root = options.output
        source_root = options.output

    validate_relative_path(options.subdir, "subdir")

    if options.include_prefix is not None:
        validate_relative_path(options.include_prefix, "include_prefix")

    header = header_root / options.subdir / f"{options.name}.h"
    source = source_root / options.subdir / f"{options.name}.cpp"

    include_path = ((options.include_prefix or Path()) / options.subdir / f"{options.name}.h")

    return CppPaths(header=header, source=source, include=include_path.as_posix())

def generate_header(name: str, namespace: str) -> str:
    """Generate a C++ class header."""

    indent = "    " if namespace else ""
    namespace_open = f"namespace {namespace}\n{{\n" if namespace else ""
    namespace_close = "}\n" if namespace else ""

    return (
        "#pragma once\n"
        "\n"
        f"{namespace_open}"
        f"{indent}class {name}\n"
        f"{indent}{{\n"
        f"{indent}public:\n"
        f"{indent}    {name}();\n"
        f"{indent}    ~{name}();\n"
        f"{indent}}};\n"
        f"{namespace_close}"
    )

def generate_source(name: str, namespace: str, include: str, local_include: bool = False) -> str:
    """Generate a C++ class implementation."""

    indent = "    " if namespace else ""
    namespace_open = f"namespace {namespace}\n{{\n" if namespace else ""
    namespace_close = "}\n" if namespace else ""

    include_statement = (f'#include "{include}"' if local_include else f"#include <{include}>")

    return (
        f"{include_statement}\n"
        "\n"
        f"{namespace_open}"
        f"{indent}{name}::{name}() = default;\n"
        "\n"
        f"{indent}{name}::~{name}() = default;\n"
        f"{namespace_close}"
    )

def generate_cpp_files(options: CppOptions) -> list[GeneratedFile]:
    """Prepare a C++ header/source pair without writing files."""

    validate_cpp_options(options)

    paths = resolve_paths(options)

    return [
        GeneratedFile(
            path=paths.header,
            content=generate_header(options.name, options.namespace)
        ),
        GeneratedFile(
            path=paths.source,
            content=generate_source(
                options.name,
                options.namespace,
                (
                    paths.header.name
                    if options.include_prefix is None and not options.split
                    and options.header_root is None
                    else paths.include
                ),
                local_include=(
                    options.include_prefix is None
                    and not options.split
                    and options.header_root is None
                ),
            ),
        )
    ]