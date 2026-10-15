
import unittest
import tempfile
from pathlib import Path

from conjure.profiles import CppProfile, load_cpp_profile, create_cpp_options, find_project_config, compose_namespace


class CppProfileTests(unittest.TestCase):
    def test_profile_stores_configuration(self):
        profile = CppProfile(
            namespace="Lunaforge::Core",
            header_root=Path("Source/Runtime/Core/Public/Lunaforge/Core"),
            source_root=Path("Source/Runtime/Private"),
            include_prefix=Path("Lunaforge/Core")
        )

        self.assertEqual(profile.namespace, "Lunaforge::Core")
        self.assertEqual(
            profile.source_root,
            Path("Source/Runtime/Private")
        )
        self.assertEqual(
            profile.include_prefix,
            Path("Lunaforge/Core")
        )

    def test_loads_cpp_profile_from_toml(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                """
                [profiles.lunaforge-core]
                namespace = "Lunaforge::Core"
                header_root = "Source/Runtime/Core/Public/Lunaforge/Core"
                source_root = "Source/Runtime/Private"
                include_prefix = "Lunaforge/Core"
                """,
                encoding="utf-8"
            )

            profile = load_cpp_profile(config_path, "lunaforge-core")

            self.assertEqual(profile.namespace, "Lunaforge::Core")
            self.assertEqual(
                profile.header_root,
                root / "Source/Runtime/Core/Public/Lunaforge/Core"
            )
            self.assertEqual(
                profile.source_root,
                root / "Source/Runtime/Private"
            )
            self.assertEqual(
                profile.include_prefix,
                Path("Lunaforge/Core")
            )
    
    def test_profile_creates_cpp_options(self):
        profile = CppProfile(
            namespace="Lunaforge::Core",
            header_root=Path("Public"),
            source_root=Path("Private"),
            include_prefix=Path("Lunaforge/Core"),
        )

        options = create_cpp_options(
            profile,
            name="Logger",
            subdir=Path("Logging"),
        )

        self.assertEqual(options.name, "Logger")
        self.assertEqual(options.namespace, "Lunaforge::Core")
        self.assertEqual(options.header_root, Path("Public"))
        self.assertEqual(options.source_root, Path("Private"))
        self.assertEqual(options.subdir, Path("Logging"))
        self.assertEqual(options.include_prefix, Path("Lunaforge/Core"))

    def test_finds_project_config_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            config_path = root / ".conjure.toml"
            config_path.write_text(
                "[profiles.test]\n",
                encoding="utf-8",
            )

            nested_directory = root / "Source" / "Runtime" / "Core"
            nested_directory.mkdir(parents=True)

            found = find_project_config(nested_directory)

            self.assertEqual(found, config_path)

    def test_compose_namespace(self):
        self.assertEqual(
            compose_namespace("Lunaforge::Core", "Logging"),
            "Lunaforge::Core::Logging",
        )

        self.assertEqual(
            compose_namespace("Lunaforge::Core", "Application::Events"),
            "Lunaforge::Core::Application::Events",
        )

        self.assertEqual(
            compose_namespace("", "Game::Systems"),
            "Game::Systems",
        )

        self.assertEqual(
            compose_namespace("Lunaforge::Core", ""),
            "Lunaforge::Core",
        )

    def test_profile_appends_namespace(self):
        profile = CppProfile(
            namespace="Lunaforge::Core",
        )

        options = create_cpp_options(
            profile,
            name="Logger",
            subdir=Path("Logging"),
            namespace_append="Logging",
        )

        self.assertEqual(
            options.namespace,
            "Lunaforge::Core::Logging",
        )

        self.assertEqual(
            options.subdir,
            Path("Logging"),
        )

    def test_rejects_incomplete_custom_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                """
                [profiles.broken]
                header_root = "Public"
                """,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "specified together"):
                load_cpp_profile(config_path, "broken")


    def test_rejects_split_with_custom_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config_path = root / ".conjure.toml"

            config_path.write_text(
                """
                [profiles.broken]
                split = true
                header_root = "Public"
                source_root = "Private"
                """,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "cannot be combined"):
                load_cpp_profile(config_path, "broken")


if __name__ == "__main__":
    unittest.main()
