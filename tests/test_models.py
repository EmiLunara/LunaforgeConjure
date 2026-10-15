import unittest
from pathlib import Path

from conjure.models import GeneratedFile

class GeneratedFileTests(unittest.TestCase):
    def test_generated_file_stores_data(self):
        generated = GeneratedFile(
            path=Path("Renderer.h"),
            content="#pragma once\n"
        )

        self.assertEqual(generated.path, Path("Renderer.h"))
        self.assertEqual(generated.content, "#pragma once\n")

if __name__ == "__main__":
    unittest.main()
