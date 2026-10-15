from collections.abc import Iterable
from pathlib import Path

from conjure.models import GeneratedFile

def write_generated_files(files: Iterable[GeneratedFile]) -> None:
    """Write generated text files without overwriting existing files."""

    generated_files = list(files)

    # Reject duplicate destinations within the generation plan.
    paths = [file.path.resolve() for file in generated_files]

    if len(paths) != len(set(paths)):
        raise ValueError("Generation plan contains duplicate destinations.")

    # Check all destinations before writing anything.
    for file in generated_files:
        if file.path.exists():
            raise FileExistsError(f"File already exists: {file.path}")

    created_files: list[Path] = []

    try:
        for file in generated_files:
            file.path.parent.mkdir(parents=True, exist_ok=True)

            # Exclusive creation protects existing files.
            with file.path.open("x", encoding="utf-8", newline="\n") as output:
                created_files.append(file.path)
                output.write(file.content)

    except OSError:
        # Best-effort rollback of files created during this operation.
        for path in reversed(created_files):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                # Preserve the original generation failure.
                pass

        raise