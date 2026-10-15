# 🌙 Lunaforge Conjure

**An extensible, IDE-independent file generation toolkit for developers.**

Lunaforge Conjure is an open-source command-line utility for generating boilerplate source files with consistent naming, namespaces, and directory structures.

Originally developed as part of the Lunaforge development ecosystem, Conjure is designed to work independently of any particular engine, IDE, or project.

**Version:** 0.1.0 (Alpha)  
**Language:** Python 3.11+  
**License:** MIT

## ✨ Features

- Generate C++ class header (`.h`) and implementation (`.cpp`) pairs.
- Configure namespaces, directory layouts, and include paths.
- Support flat, Public/Private, and custom directory structures.
- Define reusable project profiles using `.conjure.toml`.
- Extend profile namespaces for individual classes.
- Automatically discover project configurations in parent directories.
- Preview generated destinations using `--dry-run`.
- Prevent accidental overwriting of existing files.
- Generate UTF-8 text files with LF line endings.
- Integrate with VS Code or other tools through the CLI.
- Extend the toolkit with additional generators in future versions.

## 📦 Installation

### Requirements

- Python 3.11 or newer
- pip

### Install from source

Clone the repository:

```bash
git clone https://github.com/EmiLunara/LunaforgeConjure.git
cd LunaforgeConjure
```

Install in editable mode:

```bash
python -m pip install -e .
```

Editable installation is particularly useful for development because changes to the Python source files are immediately available to the installed command.

Verify installation:

```bash
conjure --help
```

**Note:** If `conjure` is not recognized, ensure your Python scripts directory is included in your system PATH.

## 🚀 Quick Start

### Generate a C++ class

```bash
conjure cpp class Renderer
```

Creates:

```text
Renderer.h
Renderer.cpp
```

Generated header:

```cpp
#pragma once

class Renderer
{
public:
    Renderer();
    ~Renderer();
};
```

Generated implementation:

```cpp
#include "Renderer.h"

Renderer::Renderer() = default;

Renderer::~Renderer() = default;
```

### Generate with a namespace

```bash
conjure cpp class Renderer --namespace Lunaforge::Graphics
```

The generated class will use:

```cpp
namespace Lunaforge::Graphics
{
    class Renderer
    {
    public:
        Renderer();
        ~Renderer();
    };
}
```

### Specify an output directory

```bash
conjure cpp class Renderer --output Source/Graphics
```

Creates both files in `Source/Graphics`.

### Generate a Public/Private layout

```bash
conjure cpp class Renderer --output Source --split
```

Creates:

```text
Source/
├── Public/
│   └── Renderer.h
└── Private/
    └── Renderer.cpp
```

### Use custom directories

```bash
conjure cpp class Logger --header-root Source/Public --source-root Source/Private --subdir Logging --include-prefix Lunaforge/Core
```

Creates:

```text
Source/
├── Public/
│   └── Logging/
│       └── Logger.h
└── Private/
    └── Logging/
        └── Logger.cpp
```

The source includes:

```cpp
#include <Lunaforge/Core/Logging/Logger.h>
```

Projects using custom include prefixes must configure their compiler's include directories accordingly.

## ⚙️ Project Profiles

Conjure supports reusable project configurations through `.conjure.toml`.

This avoids repeatedly specifying lengthy directory paths and namespace conventions.

### Create a configuration

Place `.conjure.toml` in your project's root directory.

```toml
[profiles.core]
namespace = "Lunaforge::Core"
header_root = "Source/Runtime/Core/Public/Lunaforge/Core"
source_root = "Source/Runtime/Private"
include_prefix = "Lunaforge/Core"

[profiles.graphics]
namespace = "Lunaforge::Graphics"
output = "Source/Graphics"
split = true
```

Profiles are named configurations. A project may contain multiple profiles.

Relative output directories and custom roots are resolved against the directory containing `.conjure.toml`.

### Generate using a profile

```bash
conjure cpp class Logger --profile core --subdir Logging
```

The `core` profile determines the base namespace and file layout.

### Extend a namespace

Use `--namespace-append` to extend a profile's namespace without creating additional profiles.

```bash
conjure cpp class Logger --profile core --subdir Logging --namespace-append Logging
```

Resulting namespace:

```cpp
namespace Lunaforge::Core::Logging
{
    // Generated class
}
```

Namespace extensions may contain multiple components:

```bash
--namespace-append Application::Events
```

Folder layout and namespaces remain independent; `--subdir` does not automatically change the namespace.

### Automatic configuration discovery

Conjure searches for `.conjure.toml` starting in the current working directory and continuing upward through parent directories.

For example:

```text
MyProject/
├── .conjure.toml
└── Source/
    └── Runtime/
```

Commands executed from either `MyProject` or `MyProject/Source/Runtime` can use the same project configuration.

The nearest configuration file takes precedence.

### Profile argument rules

When using `--profile`, layout and base namespace settings come from the selected profile.

The following explicit arguments cannot be combined with `--profile`:

- `--output`
- `--split`
- `--header-root`
- `--source-root`
- `--include-prefix`
- `--namespace`

You can still specify `--subdir`, `--namespace-append`, and `--dry-run`.

## 🔍 Dry Run

Preview where files would be generated without writing anything:

```bash
conjure cpp class Logger --profile core --subdir Logging --dry-run
```

Dry-run performs normal generation validation and displays the destination paths.

It does not guarantee that subsequent file creation will succeed, including when files already exist or permissions prevent writing.

## 🛡️ File Safety

Conjure is designed to avoid unintentionally modifying existing source files.

The writer:

- Rejects duplicate output destinations.
- Checks whether destination files already exist.
- Uses exclusive file creation to prevent overwriting.
- Attempts to remove files created during a failed generation operation.
- Writes text using UTF-8 encoding and LF line endings.

Rollback is best-effort rather than a full filesystem transaction.

Conjure also validates C++ identifiers, namespaces, and relative subdirectory/include-prefix arguments.

## 🧑‍💻 IDE Integration

Conjure is independent of any specific IDE.

Because it provides a command-line interface, it can be invoked through terminal commands, build scripts, editor tasks, or external development tools.

### Visual Studio Code

Conjure can be integrated into VS Code using `tasks.json`.

For example, a profile-based dry-run task:

```json
{
    "label": "Conjure: C++ Class (Profile - Dry Run)",
    "type": "process",
    "command": "conjure",
    "args": [
        "cpp",
        "class",
        "${input:className}",
        "--profile",
        "${input:profileName}",
        "--subdir",
        "${input:profileSubdir}",
        "--namespace-append",
        "${input:namespaceAppend}",
        "--dry-run"
    ],
    "options": {
        "cwd": "${workspaceFolder}"
    },
    "problemMatcher": []
}
```

Define matching `promptString` inputs in your VS Code task configuration.

Removing `--dry-run` enables actual file creation.

## 🏗️ Project Structure

```text
LunaforgeConjure/
├── conjure.py
├── pyproject.toml
├── README.md
├── LICENSE
├── conjure/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── profiles.py
│   ├── writer.py
│   └── generators/
│       ├── __init__.py
│       └── cpp.py
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_cpp.py
    ├── test_models.py
    ├── test_profiles.py
    └── test_writer.py
```

The architecture separates generation from filesystem operations.

Generators produce `GeneratedFile` descriptions, and a shared writer handles file creation.

This makes it possible to introduce other language generators without replacing the file-writing system.

## 🧪 Development and Testing

Run the automated tests from the project root:

```bash
python -m unittest discover -s tests -v
```

On Windows:

```powershell
py -m unittest discover -s tests -v
```

The test suite covers CLI behavior, file generation, directory layouts, project profiles, validation, overwrite protection, and rollback behavior.

## 🗺️ Roadmap

Potential future improvements include:

- Additional C++ file types, such as structs, interfaces, and enums.
- Support for other programming languages and resource types.
- More advanced project configuration and templates.
- Optional interactive CLI workflows.
- Enhanced VS Code integration.
- Additional cross-platform testing and compatibility improvements.
- Integration with other tools in the Lunaforge ecosystem.

These are potential directions, not guaranteed release commitments.

## 🤝 Contributing

Contributions, suggestions, bug reports, and forks are welcome!

Lunaforge Conjure is developed primarily around the needs and direction of the Lunaforge ecosystem. Contributions to the official repository are reviewed according to those priorities.

Feel free to experiment with your own forks and adapt Conjure to your development workflow.

## 📄 License

Lunaforge Conjure is released under the **MIT License**.

See [LICENSE](LICENSE) for the complete license terms.

---

**Created and maintained by EmiLunara.**

*Part of the Lunaforge ecosystem. Built for developers who love making things.* 🌙
