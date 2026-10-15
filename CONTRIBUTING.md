# Contributing to Lunaforge Conjure 🌙

Thank you for your interest in contributing to Lunaforge Conjure!

Conjure is an open-source, IDE-independent file generation toolkit. Contributions, feedback, bug reports, and suggestions are welcome.

## Project Philosophy

Lunaforge Conjure is developed primarily to support the Lunaforge development ecosystem, while remaining useful as a standalone tool.

The official repository follows the maintainer's development priorities and architectural decisions. Not every suggested feature or pull request will necessarily be accepted.

Forking and experimenting with your own versions is encouraged!

## Getting Started

1. Fork and clone the repository.
2. Create a branch for your change.
3. Install the project in editable mode:

   ```bash
   python -m pip install -e .
   ```

4. Make your changes.
5. Run the automated tests:

   ```bash
   python -m unittest discover -s tests -v
   ```

6. Open a pull request describing your changes.

Python 3.11 or newer is required.

## Development Guidelines

- Keep generators independent of the shared file writer.
- Prefer small, focused changes over unnecessary architectural complexity.
- Add or update tests when changing functionality.
- Avoid introducing external dependencies without a clear benefit.
- Preserve existing CLI behavior unless a breaking change has been discussed.
- Use forward slashes in generated C++ include paths.
- Keep code readable, consistent, and documented where appropriate.

## Reporting Bugs

When opening a bug report, please include:

- A description of the issue.
- Steps to reproduce it.
- Expected and actual behavior.
- Your operating system and Python version.
- Relevant error messages or command output.

Please avoid including passwords, private files, or sensitive project information.

## Suggesting Features

Feature suggestions are welcome!

Explain the problem you're trying to solve, your proposed approach, and how it would benefit Conjure's users.

For larger changes, consider opening an issue before beginning implementation.

## Pull Requests

Please keep pull requests focused and describe what they change.

Before submitting, ensure that the relevant tests pass. New generators should follow the existing separation between generation logic and filesystem operations.

Contributions may be reviewed, revised, accepted, or declined based on the direction of the official project.

## License

By contributing, you agree that your contributions will be distributed under the project's MIT License.

See [LICENSE](LICENSE) for details.

---

Thank you for helping make Lunaforge Conjure better! 🩷
