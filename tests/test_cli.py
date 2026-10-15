
import tempfile
import unittest
import io
import os
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

from conjure.cli import create_parser, main


class CliTests(unittest.TestCase):
    def test_parses_cpp_class_arguments(self):
        parser = create_parser()

        args = parser.parse_args([
            "cpp",
            "class",
            "Renderer",
            "--namespace", "Lunaforge::Graphics",
            "--split",
            "--include-prefix", "Lunaforge/Graphics"
        ])

        self.assertEqual(args.language, "cpp")
        self.assertEqual(args.command, "class")
        self.assertEqual(args.name, "Renderer")
        self.assertEqual(args.namespace, "Lunaforge::Graphics")
        self.assertTrue(args.split)
        self.assertEqual(
            args.include_prefix,
            Path("Lunaforge/Graphics")
        )

    def test_requires_class_name(self):
        parser = create_parser()

        with self.assertRaises(SystemExit) as context:
            parser.parse_args(["cpp", "class"])

        self.assertEqual(context.exception.code, 2)

    def test_rejects_unknown_language(self):
        parser = create_parser()

        with self.assertRaises(SystemExit) as context:
            parser.parse_args(["python", "class", "Example"])

        self.assertEqual(context.exception.code, 2)
 
    def test_generates_cpp_class(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            main([
                "cpp",
                "class",
                "TestRenderer",
                "--namespace",
                "Lunaforge::Graphics",
                "--output",
                str(root),
                "--split"
            ])

            header = root / "Public" / "TestRenderer.h"
            source = root / "Private" / "TestRenderer.cpp"

            self.assertTrue(header.is_file())
            self.assertTrue(source.is_file())

            self.assertIn(
                "class TestRenderer",
                header.read_text(encoding="utf-8")
            )

            self.assertIn(
                "TestRenderer::TestRenderer() = default;",
                source.read_text(encoding="utf-8")
            )

            self.assertNotIn(b"\r\n", header.read_bytes())
            self.assertNotIn(b"\r\n", source.read_bytes())
         
    def test_dry_run_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "Generated"

            buffer = io.StringIO()

            with redirect_stdout(buffer):
                main([
                    "cpp",
                    "class",
                    "TestRenderer",
                    "--output",
                    str(output),
                    "--split",
                    "--dry-run"
                ])

            self.assertFalse(output.exists())

            result = buffer.getvalue()

            self.assertIn("Dry run", result)
            self.assertIn("TestRenderer.h", result)
            self.assertIn("TestRenderer.cpp", result)
      
    def test_parses_cpp_profile_argument(self):
        parser = create_parser()

        args = parser.parse_args([
            "cpp",
            "class",
            "Logger",
            "--profile",
            "lunaforge-core",
        ])

        self.assertEqual(args.name, "Logger")
        self.assertEqual(args.profile, "lunaforge-core")


    def test_generates_class_using_project_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            (root / ".conjure.toml").write_text(
                """
                [profiles.core]
                namespace = "Lunaforge::Core"
                header_root = "Public"
                source_root = "Private"
                include_prefix = "Lunaforge/Core"
                """,
                encoding="utf-8",
            )

            with patch("conjure.cli.find_project_config", return_value=root / ".conjure.toml"):
                main([
                    "cpp",
                    "class",
                    "Logger",
                    "--profile",
                    "core",
                    "--subdir",
                    "Logging",
                ])

            header = root / "Public" / "Logging" / "Logger.h"
            source = root / "Private" / "Logging" / "Logger.cpp"

            self.assertTrue(header.is_file())
            self.assertTrue(source.is_file())

            self.assertIn(
                "#include <Lunaforge/Core/Logging/Logger.h>",
                source.read_text(encoding="utf-8"),
            )
            
    def test_rejects_namespace_override_with_profile(self):
        with self.assertRaises(SystemExit) as context:
            main([
                "cpp",
                "class",
                "Logger",
                "--profile",
                "core",
                "--namespace",
                "SomethingElse",
            ])

        self.assertEqual(context.exception.code, 2)

    def test_rejects_malformed_profile_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                '[profiles.core\nnamespace = "Lunaforge::Core"',
                encoding="utf-8",
            )

            with patch(
                "conjure.cli.find_project_config",
                return_value=config_path,
            ):
                with self.assertRaises(SystemExit) as context:
                    main([
                        "cpp",
                        "class",
                        "Logger",
                        "--profile",
                        "core",
                    ])

            self.assertEqual(context.exception.code, 2)
            self.assertFalse((root / "Logger.h").exists())
            self.assertFalse((root / "Logger.cpp").exists())

    def test_rejects_output_override_with_profile(self):
        with self.assertRaises(SystemExit) as context:
            main([
                "cpp",
                "class",
                "Logger",
                "--profile",
                "core",
                "--output",
                "SomeFolder",
            ])

        self.assertEqual(context.exception.code, 2)

    def test_generates_class_with_appended_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                """
                [profiles.core]
                namespace = "Lunaforge::Core"
                header_root = "Public"
                source_root = "Private"
                include_prefix = "Lunaforge/Core"
                """,
                encoding="utf-8",
            )

            with patch(
                "conjure.cli.find_project_config",
                return_value=config_path,
            ):
                main([
                    "cpp",
                    "class",
                    "Logger",
                    "--profile",
                    "core",
                    "--subdir",
                    "Logging",
                    "--namespace-append",
                    "Logging",
                ])

            header = root / "Public" / "Logging" / "Logger.h"
            source = root / "Private" / "Logging" / "Logger.cpp"

            self.assertTrue(header.is_file())
            self.assertTrue(source.is_file())

            self.assertIn(
                "namespace Lunaforge::Core::Logging",
                header.read_text(encoding="utf-8"),
            )

    def test_profile_dry_run_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                """
                [profiles.core]
                namespace = "Lunaforge::Core"
                header_root = "Public"
                source_root = "Private"
                include_prefix = "Lunaforge/Core"
                """,
                encoding="utf-8",
            )

            with patch(
                "conjure.cli.find_project_config",
                return_value=config_path,
            ):
                main([
                    "cpp",
                    "class",
                    "TestLogger",
                    "--profile",
                    "core",
                    "--subdir",
                    "Logging",
                    "--namespace-append",
                    "Logging",
                    "--dry-run",
                ])

            self.assertFalse(
                (root / "Public" / "Logging" / "TestLogger.h").exists()
            )
            self.assertFalse(
                (root / "Private" / "Logging" / "TestLogger.cpp").exists()
            )


if __name__ == "__main__":
    unittest.main()
