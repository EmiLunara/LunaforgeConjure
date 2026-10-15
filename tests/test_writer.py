
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from conjure.models import GeneratedFile
from conjure.writer import write_generated_files


class WriterTests(unittest.TestCase):
    def test_writes_multiple_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            files = [
                GeneratedFile(
                    path=root / "Public" / "Renderer.h",
                    content="#pragma once\n"
                ),
                GeneratedFile(
                    path=root / "Private" / "Renderer.cpp",
                    content='#include "Renderer.h"\n'
                )
            ]

            write_generated_files(files)

            self.assertEqual(
                (root / "Public" / "Renderer.h").read_bytes(),
                b"#pragma once\n"
            )

            self.assertEqual(
                (root / "Private" / "Renderer.cpp").read_bytes(),
                b'#include "Renderer.h"\n'
            )

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / "Existing.h"
            existing.write_text("Original content", encoding="utf-8")

            files = [
                GeneratedFile(
                    path=root / "New.cpp",
                    content="New content\n"
                ),
                GeneratedFile(
                    path=existing,
                    content="Replacement content\n"
                )
            ]

            with self.assertRaises(FileExistsError):
                write_generated_files(files)

            self.assertEqual(
                existing.read_text(encoding="utf-8"),
                "Original content"
            )

            self.assertFalse((root / "New.cpp").exists())

    def test_rejects_duplicate_destinations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Test.h"

            files = [
                GeneratedFile(path=path, content="First\n"),
                GeneratedFile(path=path, content="Second\n")
            ]

            with self.assertRaises(ValueError):
                write_generated_files(files)


    def test_rolls_back_when_later_file_cannot_be_created(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            first = root / "First.h"
            blocked = root / "Blocked"

            # A file occupies the parent directory name.
            blocked.write_text("Not a directory", encoding="utf-8")

            second = blocked / "Second.cpp"

            files = [
                GeneratedFile(first, "header"),
                GeneratedFile(second, "source"),
            ]

            with self.assertRaises(OSError):
                write_generated_files(files)

            self.assertFalse(first.exists())
            self.assertFalse(second.exists())
            self.assertEqual(
                blocked.read_text(encoding="utf-8"),
                "Not a directory",
            )

if __name__ == "__main__":
    unittest.main()
