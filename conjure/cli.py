import argparse
import tomllib
from pathlib import Path

from conjure.generators.cpp import CppOptions, generate_cpp_files
from conjure.writer import write_generated_files
from conjure.profiles import create_cpp_options, find_project_config, load_cpp_profile

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="conjure", description="Lunaforge Conjure - A modular file generation toolkit.", epilog="Generate project files using explicit options or reusable project profiles.")

    languages = parser.add_subparsers(dest="language", required=True, metavar="LANGUAGE")

    cpp_parser = languages.add_parser("cpp", help="Generate C++ source files.", description="Generate C++ source files using configurable layouts.")

    cpp_commands = cpp_parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    class_parser = cpp_commands.add_parser("class", help="Generate a C++ class header/source pair.", description="Generate a C++ class with configurable namespaces, directories, and includes.", epilog="Example: conjure cpp class Logger --profile core --subdir Logging --namespace-append Logging")

    class_parser.add_argument("name", help="Name of the C++ class to generate.")

    layout = class_parser.add_argument_group("File layout")

    layout.add_argument("--output", type=Path, default=None, metavar="DIR", help="Base output directory for flat or split layouts (default: current directory).")
    layout.add_argument("--split", action="store_true", help="Separate generated headers and sources into Public/Private directories.")
    layout.add_argument("--header-root", type=Path, metavar="DIR", help="Custom root directory for generated headers.")
    layout.add_argument("--source-root", type=Path, metavar="DIR", help="Custom root directory for generated source files.")
    layout.add_argument("--subdir", type=Path, default=Path("."), metavar="DIR", help="Relative subdirectory appended to the header and source roots.")
    layout.add_argument("--include-prefix", type=Path, metavar="PATH", help="Logical include path prefix for generated C++ includes.")

    namespaces = class_parser.add_argument_group("Namespaces")

    namespaces.add_argument("--namespace", default="", metavar="NAME", help="Full C++ namespace for generation without a profile (e.g. Game::Rendering).")
    namespaces.add_argument("--namespace-append", type=str, default="", metavar="NAME", help="Namespace extension appended to the selected profile's base namespace.")

    profiles = class_parser.add_argument_group("Project profiles")

    profiles.add_argument("--profile", type=str, metavar="NAME", help="Named profile from the nearest .conjure.toml in the current directory or its parents.")

    execution = class_parser.add_argument_group("Execution")

    execution.add_argument("--dry-run", action="store_true", help="Preview destination paths without creating files.")

    return parser

def main(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.language == "cpp" and args.command == "class":
        if args.profile:
            conflicting_options = []

            if args.namespace:
                conflicting_options.append("--namespace")

            if args.split:
                conflicting_options.append("--split")

            if args.header_root is not None:
                conflicting_options.append("--header-root")

            if args.source_root is not None:
                conflicting_options.append("--source-root")

            if args.include_prefix is not None:
                conflicting_options.append("--include-prefix")

            if args.output is not None:
                conflicting_options.append("--output")

            if conflicting_options:
                parser.error("The following options cannot be combined with --profile: " + ", ".join(conflicting_options))

            config_path = find_project_config()

            if config_path is None:
                parser.error("Could not find .conjure.toml in the current directory or any parent directory.")

            try:
                profile = load_cpp_profile(config_path, args.profile)
            except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
                parser.error(f"Could not load Conjure profile: {error}")

            options = create_cpp_options(profile, name=args.name, subdir=args.subdir, namespace_append=args.namespace_append)

        else:
            if args.namespace_append:
                parser.error("--namespace-append requires --profile.")

            options = CppOptions(
                name=args.name,
                namespace=args.namespace,
                output=args.output if args.output is not None else Path("."),
                split=args.split,
                header_root=args.header_root,
                source_root=args.source_root,
                subdir=args.subdir,
                include_prefix=args.include_prefix
            )

        try:
            files = generate_cpp_files(options)

            if args.dry_run:
                print("Dry run - no files will be created.")
                print("\nWould generate:")

                for file in files:
                    print(f" {file.path}")

                return
            
            write_generated_files(files)
        except (OSError, ValueError) as error:
            parser.exit(1, f"conjure: generation failed: {error}\n")

        print("Successfully generated:")
        for file in files:
            print(f" {file.path}")