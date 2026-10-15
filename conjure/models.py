from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class GeneratedFile:
    """
    Represents a text file produced by a generator.

    The model describes what should be generated,
    without performing any filesystem operations.
    """

    path: Path
    content: str