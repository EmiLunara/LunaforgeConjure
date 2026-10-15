
import unittest
from pathlib import Path
import tempfile

from conjure.generators.cpp import CppOptions, resolve_paths, generate_cpp_files
from conjure.writer import write_generated_files


class CppPathTests(unittest.TestCase):
    def test_flat_layout(self):
        options = CppOptions(
            name="Renderer",
            output=Path("Output")
        )

        paths = resolve_paths(options)

        self.assertEqual(paths.header, Path("Output/Renderer.h"))
        self.assertEqual(paths.source, Path("Output/Renderer.cpp"))
        self.assertEqual(paths.include, "Renderer.h")

    def test_split_layout(self):
        options = CppOptions(
            name="Renderer",
            output=Path("Output"),
            split=True
        )

        paths = resolve_paths(options)

        self.assertEqual(paths.header, Path("Output/Public/Renderer.h"))
        self.assertEqual(paths.source, Path("Output/Private/Renderer.cpp"))
        self.assertEqual(paths.include, "Renderer.h")

    def test_custom_layout(self):
        options = CppOptions(
            name="Logger",
            namespace="Lunaforge::Core::Logging",
            header_root=Path(
                "Source/Runtime/Core/Public/Lunaforge/Core"
            ),
            source_root=Path("Source/Runtime/Private"),
            subdir=Path("Logging"),
            include_prefix=Path("Lunaforge/Core")
        )

        paths = resolve_paths(options)

        self.assertEqual(
            paths.header,
            Path(
                "Source/Runtime/Core/Public/"
                "Lunaforge/Core/Logging/Logger.h"
            )
        )

        self.assertEqual(
            paths.source,
            Path("Source/Runtime/Private/Logging/Logger.cpp")
        )

        self.assertEqual(
            paths.include,
            "Lunaforge/Core/Logging/Logger.h"
        )

    
    def test_generates_cpp_file_pair(self):
        options = CppOptions(
            name="Renderer",
            namespace="Lunaforge::Graphics",
            output=Path("Output")
        )

        files = generate_cpp_files(options)

        self.assertEqual(len(files), 2)

        header, source = files

        self.assertEqual(header.path, Path("Output/Renderer.h"))
        self.assertEqual(source.path, Path("Output/Renderer.cpp"))

        self.assertIn("#pragma once", header.content)
        self.assertIn("class Renderer", header.content)
        self.assertIn("namespace Lunaforge::Graphics", header.content)
        self.assertIn("Renderer();", header.content)

        self.assertIn('#include "Renderer.h"', source.content)
        self.assertIn("Renderer::Renderer() = default;", source.content)
        self.assertIn("Renderer::~Renderer() = default;", source.content)

        self.assertTrue(header.content.endswith("\n"))
        self.assertTrue(source.content.endswith("\n"))

    def test_generates_and_writes_cpp_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            options = CppOptions(
                name="Renderer",
                namespace="Lunaforge::Graphics",
                output=root,
                split=True
            )

            # Generate the file descriptions.
            files = generate_cpp_files(options)

            # Write them using our shared filesystem writer.
            write_generated_files(files)

            header = root / "Public" / "Renderer.h"
            source = root / "Private" / "Renderer.cpp"

            self.assertTrue(header.is_file())
            self.assertTrue(source.is_file())

            self.assertIn(
                "class Renderer",
                header.read_text(encoding="utf-8")
            )

            self.assertIn(
                "#include <Renderer.h>",
                source.read_text(encoding="utf-8")
            )

            # Verify Unix LF line endings.
            self.assertNotIn(b"\r\n", header.read_bytes())
            self.assertNotIn(b"\r\n", source.read_bytes())

    
    def test_rejects_invalid_class_names(self):
        invalid_names = [
            "",
            "123Renderer",
            "My Class",
            "class",
            "namespace",
            "_Internal",
            "My__Class"
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    generate_cpp_files(CppOptions(name=name))


    def test_rejects_invalid_namespaces(self):
        invalid_namespaces = [
            "Lunaforge::123Graphics",
            "Lunaforge::class",
            "Lunaforge::::Graphics",
            "::Lunaforge",
            "Lunaforge::"
        ]

        for namespace in invalid_namespaces:
            with self.subTest(namespace=namespace):
                with self.assertRaises(ValueError):
                    generate_cpp_files(
                        CppOptions(
                            name="Renderer",
                            namespace=namespace
                        )
                    )
    
    def test_rejects_unsafe_subdirectories(self):
        unsafe_paths = [
            Path("../Outside"),
            Path("Logging/../../Outside"),
            Path("C:RelativePath"),
            Path("C:/AbsolutePath")
        ]

        for path in unsafe_paths:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    generate_cpp_files(
                        CppOptions(
                            name="Renderer",
                            subdir=path
                        )
                    )


    def test_rejects_unsafe_include_prefixes(self):
        unsafe_paths = [
            Path("../Outside"),
            Path("Lunaforge/../../Outside"),
            Path("C:RelativePath"),
            Path("C:/AbsolutePath")
        ]

        for path in unsafe_paths:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    generate_cpp_files(
                        CppOptions(
                            name="Renderer",
                            include_prefix=path
                        )
                    )

    def test_rejects_cpp_operator_keywords(self):
        for name in ("and", "or", "not", "xor", "bitand", "compl"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    generate_cpp_files(CppOptions(name=name))

    def test_flat_layout_uses_local_header_include(self):
        files = generate_cpp_files(
            CppOptions(
                name="Renderer",
                subdir=Path("Graphics"),
            )
        )

        source = next(
            file for file in files
            if file.path.suffix == ".cpp"
        )

        self.assertIn(
            '#include "Renderer.h"',
            source.content,
        )


if __name__ == "__main__":
    unittest.main()
